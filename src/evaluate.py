"""
模型批量评估器：加载 Base 模型或 LoRA 微调模型，在 Test Set 上批量生成并计算通过率。
"""

import json
import os
import re
from collections import Counter

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

from src.validator import validate_response

def clean_response(response: str) -> str:
    """
    清洗模型输出：
    Qwen3 默认会输出 <think>...</think> 的思考过程，需要截断，只保留最终回答。
    """
    if "</think>" in response:
        # 取 </think> 之后的文本
        response = response.split("</think>")[-1].strip()
    return response

def enforce_length_constraint(response: str, constraints: dict) -> str:
    """
    工业级后处理：如果模型回答略微超出字数上限（在容忍阈值内），
    则自动按句号截断，或者进行压缩。
    """
    if "length" not in constraints:
        return response
    
    max_len = constraints["length"]["max"]
    # 如果没超，或者超得太多（超过20%，说明完全跑题，不救），直接返回
    if len(response) <= max_len or len(response) > max_len * 1.2:
        return response
        
    # 在 max_len 范围内，寻找最后一个句号（。！？）
    truncated = response[:max_len]
    last_punctuation = max(truncated.rfind("。"), truncated.rfind("！"), truncated.rfind("？"))
    
    if last_punctuation > max_len * 0.8: # 确保截断后不会少于下限的80%
        return truncated[:last_punctuation + 1]
        
    return response

def model_generate(
    model,
    tokenizer,
    prompts: list[str],
    max_new_tokens: int = 512,
) -> list[str]:
    """
    给定一批 prompts，让模型生成回答。
    """
    # 1. 套用 Qwen 的 Chat Template
    tokenized_prompts = [
        tokenizer.apply_chat_template(
            [{"role": "user", "content": p}],
            tokenize=False,
            add_generation_prompt=True
        ) for p in prompts
    ]

    # 2. 文本 -> Token IDs
    tokenizer.padding_side = "left"
    inputs = tokenizer(
        tokenized_prompts,
        return_tensors="pt",
        padding=True,
        truncation=True,
    ).to(model.device)

    # 3. 推理
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    # 4. 只解码新生成的部分
    input_length = inputs["input_ids"].shape[1]
    generated_ids = outputs[:, input_length:]
    
    responses = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    return responses

def evaluate_model(
    model_path: str,
    test_set_path: str = "data/test.jsonl",
    adapter_path: str = None,
    output_path: str = "data/eval_results.json",
    batch_size: int = 4,
    max_new_tokens: int = 512,
) -> dict:
    """
    加载本地模型，在测试集上生成回答并用 validator 校验。
    
    - model_path: 基础模型路径（如 "Qwen/Qwen3-8B"）
    - adapter_path: LoRA adapter 路径（微调后用，Base 模型测试时传 None）
    - 返回: 评估统计字典（含通过率、分难度统计、失败模式等）

    批量评估模型表现
    """
    print(f"开始评估模型: {model_path}" + (f" (Adapter: {adapter_path})" if adapter_path else ""))

    # ============ 1. 加载模型 ============
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    # 确保有 pad_token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )

    if adapter_path:
        print(f"   -> 加载 LoRA Adapter: {adapter_path}")
        model = PeftModel.from_pretrained(base_model, adapter_path)
    else:
        model = base_model

    model.eval()

    # ============ 2. 读取测试集 ============
    with open(test_set_path, "r", encoding="utf-8") as f:
        test_samples = [json.loads(line) for line in f if line.strip()]

    print(f"   -> 共 {len(test_samples)} 条测试样本")

    # ============ 3. 批量生成与评估 ============
    valid_count = 0
    rejected_count = 0
    by_difficulty = Counter()
    total_by_difficulty = Counter()
    failure_modes = Counter()
    
    results_details = []

    for i in range(0, len(test_samples), batch_size):
        batch = test_samples[i : i + batch_size]
        prompts = [s["prompt"] for s in batch]

        # 推理
        responses = model_generate(model, tokenizer, prompts, max_new_tokens)

        # 逐条校验
        for sample, response in zip(batch, responses):
            response = clean_response(response)
            response = enforce_length_constraint(response, sample["constraints"])
            passed, violations = validate_response(response, sample["constraints"])
            
            sample_copy = sample.copy()
            sample_copy["response"] = response
            sample_copy["passed"] = passed
            sample_copy["violations"] = violations
            results_details.append(sample_copy)

            total_by_difficulty[sample["difficulty"]] += 1

            if passed:
                valid_count += 1
                by_difficulty[sample["difficulty"]] += 1
            else:
                rejected_count += 1
                # 提取失败模式关键词（复用之前的逻辑）
                for v in violations:
                    if "长度" in v: failure_modes["长度超限"] += 1
                    elif "段" in v: failure_modes["段落/句数错误"] += 1
                    elif "禁用词" in v: failure_modes["含禁用词"] += 1
                    else: failure_modes[v[:20]] += 1

        print(f"   已处理: {min(i + batch_size, len(test_samples))}/{len(test_samples)}")

    # ============ 4. 汇总统计 ============
    total = len(test_samples)
    pass_rate = round(valid_count / total * 100, 2) if total else 0.0

    # 按难度计算通过率
    diff_stats = {}
    for diff in ["simple", "medium", "hard"]:
        v = by_difficulty.get(diff, 0)
        t = total_by_difficulty.get(diff, 0)
        r = round(v / t * 100, 2) if t else 0.0
        diff_stats[diff] = {"total": t, "passed": v, "pass_rate": r}

    stats = {
        "model_path": model_path,
        "adapter_path": adapter_path,
        "total": total,
        "total_valid": valid_count,
        "total_rejected": rejected_count,
        "pass_rate": pass_rate,
        "by_difficulty": diff_stats,
        "failure_modes": dict(failure_modes),
        "details": results_details,
    }

    # ============ 5. 写出结果 ============
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print("\n评估完成")
    print(f"   总体通过率: {pass_rate}% ({valid_count}/{total})")
    for diff, ds in diff_stats.items():
        print(f"   - {diff}: {ds['pass_rate']}% ({ds['passed']}/{ds['total']})")

    return stats