# tests/test_evaluate.py
import json
import os
import pytest
from unittest.mock import patch, MagicMock
from src.evaluate import evaluate_model


@pytest.fixture
def setup_test_set(tmp_path):
    """准备一个 3 条的假测试集"""
    test_file = tmp_path / "test.jsonl"
    samples = [
        {
            "id": "test_T12_0001", "split": "test", "difficulty": "simple",
            "prompt": "请回答：为什么天是蓝的。字数80~100字。",
            "constraints": {"length": {"min": 80, "max": 100}}
        },
        {
            "id": "test_T12_0002", "split": "test", "difficulty": "medium",
            "prompt": "请回答：为什么天是蓝的。字数80~100字，分为2段。",
            "constraints": {"length": {"min": 80, "max": 100}, "paragraph": {"num_paragraphs": 2, "sentences_per_paragraph": 2}}
        },
        {
            "id": "test_T12_0003", "split": "test", "difficulty": "hard",
            "prompt": "请回答：为什么天是蓝的。字数80~100字，分为2段，禁用'因此'。",
            "constraints": {"length": {"min": 80, "max": 100}, "paragraph": {"num_paragraphs": 2, "sentences_per_paragraph": 2}, "forbidden_word": ["因此"]}
        }
    ]
    with open(test_file, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    return str(test_file)


# ============ 测试开始 ============

@patch("src.evaluate.AutoModelForCausalLM.from_pretrained")
@patch("src.evaluate.AutoTokenizer.from_pretrained")
# 自定义一个 wrapper 方便 mock
@patch("src.evaluate.model_generate")
def test_output_file_created(mock_gen, mock_tokenizer, mock_model, setup_test_set, tmp_path):
    # mock 模型输出的固定回答
    mock_gen.return_value = ["字" * 90]  # 满足第一条的长度约束
    output_path = str(tmp_path / "eval_out.json")
    
    evaluate_model(
        model_path="fake-model",
        test_set_path=setup_test_set,
        output_path=output_path,
    )
    assert os.path.exists(output_path)


@patch("src.evaluate.AutoModelForCausalLM.from_pretrained")
@patch("src.evaluate.AutoTokenizer.from_pretrained")
@patch("src.evaluate.model_generate")
def test_evaluate_calculates_correct_pass_rate(mock_gen, mock_tokenizer, mock_model, setup_test_set, tmp_path):
    # 第一条满足(90字)，第二条不满足(91字，但段落不对)，第三条不满足(有禁词)
    mock_gen.side_effect = [
        ["字" * 90], 
        ["字" * 90], # 这里假设mock不改变，但validator会判错
        ["字" * 90 + "因此"]
    ]
    output_path = str(tmp_path / "eval_out.json")
    stats = evaluate_model(
        model_path="fake-model",
        test_set_path=setup_test_set,
        output_path=output_path,
    )
    # 理论上只过了第一条
    assert stats["total_valid"] == 1
    assert stats["pass_rate"] == 33.33


@patch("src.evaluate.AutoModelForCausalLM.from_pretrained")
@patch("src.evaluate.AutoTokenizer.from_pretrained")
@patch("src.evaluate.model_generate")
def test_evaluate_includes_per_difficulty_stats(mock_gen, mock_tokenizer, mock_model, setup_test_set, tmp_path):
    mock_gen.return_value = ["字" * 90]
    output_path = str(tmp_path / "eval_out.json")
    stats = evaluate_model(model_path="fake", test_set_path=setup_test_set, output_path=output_path)
    assert "by_difficulty" in stats
    assert "simple" in stats["by_difficulty"]


@patch("src.evaluate.AutoModelForCausalLM.from_pretrained")
@patch("src.evaluate.AutoTokenizer.from_pretrained")
@patch("src.evaluate.model_generate")
def test_evaluate_includes_failure_modes(mock_gen, mock_tokenizer, mock_model, setup_test_set, tmp_path):
    mock_gen.side_effect = [["短"], ["短"], ["短"]] # 全部因长度失败
    output_path = str(tmp_path / "eval_out.json")
    stats = evaluate_model(model_path="fake", test_set_path=setup_test_set, output_path=output_path)
    assert "failure_modes" in stats
    assert stats["failure_modes"].get("长度超限", 0) > 0


@patch("src.evaluate.PeftModel.from_pretrained")
@patch("src.evaluate.AutoModelForCausalLM.from_pretrained")
@patch("src.evaluate.AutoTokenizer.from_pretrained")
@patch("src.evaluate.model_generate")
def test_adapter_path_loaded(mock_gen, mock_tokenizer, mock_model, mock_peft, setup_test_set, tmp_path):
    evaluate_model(model_path="fake", adapter_path="fake-adapter", test_set_path=setup_test_set, output_path=str(tmp_path/"out.json"))
    mock_peft.assert_called_once()


@patch("src.evaluate.PeftModel.from_pretrained")
@patch("src.evaluate.AutoModelForCausalLM.from_pretrained")
@patch("src.evaluate.AutoTokenizer.from_pretrained")
@patch("src.evaluate.model_generate")
def test_no_adapter_path_loads_base_model(mock_gen, mock_tokenizer, mock_model, mock_peft, setup_test_set, tmp_path):
    evaluate_model(model_path="fake", adapter_path=None, test_set_path=setup_test_set, output_path=str(tmp_path/"out.json"))
    mock_peft.assert_not_called()