from typing import Dict, List

def format_and_tokenize(tokenizer, prompt: str, response: str) -> Dict[str, List[int]]:
    """
    将单条 (prompt, response) 转换为带 masked labels 的 token 序列。
    """
    # 1. 构建对话格式文本
    # 使用 Qwen 的 chat template 模板
    prompt_text = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        tokenize=False,
        add_generation_prompt=True   # 这一步很重要，它会加上 <|im_start|>assistant\n
    )
    
    # response 只需要纯文本（微调时，我们希望模型直接接在 assistant 标记后输出）
    # 可以在结尾加上 eos_token，让模型学会什么时候闭嘴
    response_text = response + tokenizer.eos_token

    # 2. 分别 Tokenize
    prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    response_ids = tokenizer(response_text, add_special_tokens=False)["input_ids"]

    # 3. 拼接成完整的输入序列
    input_ids = prompt_ids + response_ids

    # 4. 构建labels：prompt 部分的 token 设为-100，response 部分保留原id
    labels = [-100]*len(prompt_ids) + response_ids

    return {
        "input_ids": input_ids,
        "labels": labels}