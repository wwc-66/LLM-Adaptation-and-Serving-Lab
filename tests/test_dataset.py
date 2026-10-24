import pytest
from transformers import AutoTokenizer
from src.dataset import format_and_tokenize

# 用全局 fixture 避免重复加载 tokenizer
@pytest.fixture(scope="module")
def tokenizer():
    # 指定 local_files_only=True，防止测试时联网
    return AutoTokenizer.from_pretrained("Qwen/Qwen3-8B", local_files_only=True, trust_remote_code=True)

def test_lengths_match(tokenizer):
    """input_ids 和 labels 长度必须完全一致"""
    prompt = "请解释天空的颜色。"
    response = "天空是蓝色的。"
    result = format_and_tokenize(tokenizer, prompt, response)
    
    assert len(result["input_ids"]) == len(result["labels"])

def test_prompt_is_masked(tokenizer):
    """prompt 部分对应的 labels 必须全是 -100"""
    prompt = "请解释天空的颜色。"
    response = "天空是蓝色的。"
    result = format_and_tokenize(tokenizer, prompt, response)
    
    # 找出第一个不是 -100 的位置（即 response 开始的位置）
    labels = result["labels"]
    first_response_idx = next(i for i, x in enumerate(labels) if x != -100)
    
    # 这个位置之前，必须全部是 -100
    assert all(x == -100 for x in labels[:first_response_idx])
    
def test_response_is_not_masked(tokenizer):
    """response 部分的 labels 必须和 input_ids 完全一致"""
    prompt = "请解释天空的颜色。"
    response = "天空是蓝色的。"
    result = format_and_tokenize(tokenizer, prompt, response)
    
    labels = result["labels"]
    input_ids = result["input_ids"]
    
    first_response_idx = next(i for i, x in enumerate(labels) if x != -100)
    
    # 这个位置之后，labels 必须等于 input_ids
    assert labels[first_response_idx:] == input_ids[first_response_idx:]