import os
import pytest
from unittest.mock import patch
from src.pipeline import run_pipeline


@pytest.fixture
def output_dir(tmp_path):
    return str(tmp_path)


# ============ A 组：端到端跑通 ============

@patch("src.pipeline.call_teacher")
def test_pipeline_runs_end_to_end(mock_teacher, output_dir):
    """全流程跑通，返回 stats"""
    mock_teacher.return_value = {
        "response": "字" * 90,
        "attempts": 1,
        "error": None,
        "latency_ms": 100.0,
    }
    stats = run_pipeline(output_dir=output_dir, n_per_family=3, limit=3)
    assert stats["total_valid"] + stats["total_rejected"] == 3


@patch("src.pipeline.call_teacher")
def test_pipeline_returns_stats_dict(mock_teacher, output_dir):
    """返回 stats 字典"""
    mock_teacher.return_value = {
        "response": "字" * 90,
        "attempts": 1,
        "error": None,
        "latency_ms": 100.0,
    }
    stats = run_pipeline(output_dir=output_dir, n_per_family=3, limit=3)
    assert "total_valid" in stats
    assert "total_rejected" in stats
    assert "by_split" in stats


# ============ B 组：样本分流 ============

@patch("src.pipeline.call_teacher")
def test_teacher_failure_goes_to_rejected(mock_teacher, output_dir):
    """teacher 调用失败 → 样本进 rejected"""
    mock_teacher.return_value = {
        "response": "",
        "attempts": 3,
        "error": "Connection timeout",
        "latency_ms": 1000.0,
    }
    stats = run_pipeline(output_dir=output_dir, n_per_family=3, limit=3)
    assert stats["total_rejected"] == 3
    assert stats["total_valid"] == 0


# ============ C 组：参数控制 ============

@patch("src.pipeline.call_teacher")
def test_limit_restricts_sample_count(mock_teacher, output_dir):
    """limit 参数限制实际处理数量"""
    mock_teacher.return_value = {
        "response": "字" * 90,
        "attempts": 1,
        "error": None,
        "latency_ms": 100.0,
    }
    stats = run_pipeline(output_dir=output_dir, n_per_family=10, limit=5)
    assert stats["total_valid"] + stats["total_rejected"] == 5


# ============ D 组：产物验证 ============

@patch("src.pipeline.call_teacher")
def test_output_files_exist(mock_teacher, output_dir):
    """生成的文件都存在"""
    mock_teacher.return_value = {
        "response": "字" * 90,
        "attempts": 1,
        "error": None,
        "latency_ms": 100.0,
    }
    run_pipeline(output_dir=output_dir, n_per_family=3, limit=3)
    for fname in ["train.jsonl", "val.jsonl", "test.jsonl", "stats.json"]:
        assert os.path.exists(os.path.join(output_dir, fname))