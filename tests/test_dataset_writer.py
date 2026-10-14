# tests/test_dataset_writer.py
import json
import os
import pytest
from src.dataset_writer import write_datasets


@pytest.fixture
def sample_dir(tmp_path):
    """每个测试用一个临时目录，避免污染真实 data/"""
    return str(tmp_path)


def _make_sample(sid, split, difficulty="simple", template="T1"):
    return {
        "id": sid,
        "template_id": template,
        "split": split,
        "style": "direct_command",
        "topic": "为什么天空是蓝色的",
        "topic_domain": "science",
        "difficulty": difficulty,
        "constraints": {"length": {"min": 80, "max": 100}},
        "prompt": "测试 prompt",
        "response": "测试 response",
    }


def _make_rejected(sid):
    return {
        "id": sid,
        "prompt": "测试 prompt",
        "response": "不合格 response",
        "violations": ["长度超限"],
    }


# ============ A 组：文件生成 ============

def test_creates_three_split_files(sample_dir):
    """三个 split 文件都被创建"""
    valid = [
        _make_sample("train_T1_0001", "train"),
        _make_sample("val_T9_0001", "val"),
        _make_sample("test_T12_0001", "test"),
    ]
    write_datasets(valid, [], sample_dir)
    for fname in ["train.jsonl", "val.jsonl", "test.jsonl"]:
        assert os.path.exists(os.path.join(sample_dir, fname))


def test_creates_rejected_and_stats(sample_dir):
    """rejected.jsonl 和 stats.json 都被创建"""
    valid = [_make_sample("train_T1_0001", "train")]
    rejected = [_make_rejected("train_T1_0002")]
    write_datasets(valid, rejected, sample_dir)
    assert os.path.exists(os.path.join(sample_dir, "rejected.jsonl"))
    assert os.path.exists(os.path.join(sample_dir, "stats.json"))


# ============ B 组：内容正确性 ============

def test_split_assignment_correct(sample_dir):
    """样本被写到正确的 split 文件"""
    valid = [
        _make_sample("train_T1_0001", "train"),
        _make_sample("train_T1_0002", "train"),
        _make_sample("val_T9_0001", "val"),
        _make_sample("test_T12_0001", "test"),
    ]
    write_datasets(valid, [], sample_dir)

    with open(os.path.join(sample_dir, "train.jsonl"), encoding="utf-8") as f:
        train_lines = f.readlines()
    with open(os.path.join(sample_dir, "val.jsonl"), encoding="utf-8") as f:
        val_lines = f.readlines()
    with open(os.path.join(sample_dir, "test.jsonl"), encoding="utf-8") as f:
        test_lines = f.readlines()

    assert len(train_lines) == 2
    assert len(val_lines) == 1
    assert len(test_lines) == 1


def test_jsonl_is_valid_json_per_line(sample_dir):
    """每行都是合法 JSON"""
    valid = [_make_sample("train_T1_0001", "train")]
    write_datasets(valid, [], sample_dir)
    with open(os.path.join(sample_dir, "train.jsonl"), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                json.loads(line)   # 不报错就通过


# ============ C 组：统计报告 ============

def test_stats_counts_correct(sample_dir):
    """stats.json 里的计数正确"""
    valid = [
        _make_sample("train_T1_0001", "train", difficulty="simple"),
        _make_sample("train_T1_0002", "train", difficulty="medium"),
        _make_sample("val_T9_0001", "val", difficulty="hard"),
    ]
    rejected = [_make_rejected("train_T1_0003")]
    stats = write_datasets(valid, rejected, sample_dir)

    assert stats["total_valid"] == 3
    assert stats["total_rejected"] == 1
    assert stats["by_split"]["train"] == 2
    assert stats["by_split"]["val"] == 1
    assert stats["by_split"]["test"] == 0
    assert stats["by_difficulty"]["simple"] == 1
    assert stats["by_difficulty"]["hard"] == 1


# ============ D 组：边界情况 ============

def test_empty_input_does_not_crash(sample_dir):
    """空输入不崩溃，仍生成空文件"""
    stats = write_datasets([], [], sample_dir)
    assert stats["total_valid"] == 0
    assert stats["total_rejected"] == 0