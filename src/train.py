import os

# 强制完全离线，禁止任何网络请求
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_DISABLE_XET"] = "1"

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from src.dataset import format_and_tokenize

def train():
    model_id = "Qwen/Qwen3-8B"
    output_dir = "./lora_adapter"
    
    print(f"开始 QLoRA 微调: {model_id}")

    # 1. 4-bit 量化配置（把显存需求降到最低）
    bnb_config = BitsAndBytesConfig(
        # 启用 4bit 量化
        load_in_4bit=True,
        # NormalFloat4 量化类型（专为 LLM 设计）
        bnb_4bit_quant_type="nf4",
        # 计算时转回 bf16，保证精度
        bnb_4bit_compute_dtype=torch.bfloat16,
        #双重量化，进一步省显存
        bnb_4bit_use_double_quant=True
    )

    # 2. LoRA 配置
    lora_config = LoraConfig(
        # 低秩矩阵的维度 Rank ，决定参数量
        r=8,
        # 缩放因子，通常设为 r 的2倍
        lora_alpha=16,
        # 注入 LoRA 的层
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        #防止过拟合
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    # 3. 加载 Tokenizer 和 4-bit 模型
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        local_files_only=True
    )
    
    # 让模型准备好进行 k-bit 训练（冻结原权重，开启梯度检查点）
    model = prepare_model_for_kbit_training(model)
    
    # 注入 LoRA 适配器
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters() # 打印出可训练参数占比（通常只有 1% 左右）

    # 4. 加载并处理数据
    print("1.正在处理训练数据")
    dataset = load_dataset("json", data_files="data/train.jsonl", split="train")

    def process_func(examples):
        results = {"input_ids": [], "labels": [], "attention_mask": []}
        for p, r in zip(examples["prompt"], examples["response"]):
            out = format_and_tokenize(tokenizer, p, r)
            results["input_ids"].append(out["input_ids"])
            results["labels"].append(out["labels"])
            results["attention_mask"].append([1] * len(out["input_ids"]))
        return results

    tokenized_dataset = dataset.map(
        process_func, 
        batched=True, 
        remove_columns=dataset.column_names
    )

    # 5. 训练参数（针对 5090 显存优化）
    training_args = TrainingArguments(
        output_dir="./results",
        per_device_train_batch_size=4,         # 单卡批大小
        gradient_accumulation_steps=2,         # 梯度累积（等效 batch_size=8）
        learning_rate=2e-4,                    # LoRA 常用学习率
        logging_steps=10,
        num_train_epochs=3,
        save_strategy="epoch",
        optim="paged_adamw_8bit",              # QLoRA 专用优化器，防止 OOM
        bf16=True,                             # 5090 完美支持 bf16
        report_to="none"                       # 不连接 wandb
    )

    # 6. 开始训练
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True),
    )

    print("2.开始训练")
    trainer.train()

    # 7. 保存模型（只保存 LoRA 权重，非常小，约 20MB）
    print("3.保存 LoRA Adapter")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("4.微调已完成")

if __name__ == "__main__":
    train()