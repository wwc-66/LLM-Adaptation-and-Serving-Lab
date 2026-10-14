import pytest
from unittest.mock import patch, MagicMock
from src.teacher_caller import call_teacher


# ============ A 组：基本调用 ============

@patch("src.teacher_caller.requests.post")
def test_successful_call_returns_response(mock_post):
    """mock 返回 '这是回答'，验证 response 字段正确，error 为 None"""
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": "这是回答"}}]
    }
    result = call_teacher("测试 prompt")
    assert result["response"] == "这是回答"
    assert result["error"] is None


@patch("src.teacher_caller.requests.post")
def test_call_records_latency(mock_post):
    """验证 latency_ms > 0"""
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": "这是回答"}}]
    }
    result = call_teacher("测试 prompt")
    assert result["latency_ms"] > 0


# ============ B 组：重试机制 ============

@patch("src.teacher_caller.requests.post")
def test_retries_on_timeout(mock_post):
    """前两次抛 TimeoutError，第三次成功 → attempts == 3"""
    # 构造一个"假响应对象"，它的 .json() 返回想要的数据
    success_response = MagicMock()
    success_response.json.return_value = {
        "choices": [{"message": {"content": "成功"}}]
    }
    # side_effect 是一个列表：按顺序，前两次抛异常，第三次返回成功对象
    mock_post.side_effect = [
        TimeoutError("第一次超时"),
        TimeoutError("第二次超时"),
        success_response,
    ]
    result = call_teacher("测试 prompt", max_retries=3)
    assert result["response"] == "成功"
    assert result["attempts"] == 3


@patch("src.teacher_caller.requests.post")
def test_gives_up_after_max_retries(mock_post):
    """永远超时 → response 为空，error 非空，attempts == max_retries"""
    mock_post.side_effect = TimeoutError("永远超时")
    result = call_teacher("测试 prompt", max_retries=3)
    assert result["response"] == ""
    assert result["error"] is not None
    assert result["attempts"] == 3


@patch("src.teacher_caller.requests.post")
def test_no_retry_on_success(mock_post):
    """一次成功 → attempts == 1"""
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": "这是回答"}}]
    }
    result = call_teacher("测试 prompt")
    assert result["attempts"] == 1