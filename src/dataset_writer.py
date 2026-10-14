"""
数据集写出：把通过的样本按 split 写入 jsonl，同时输出统计报告。
"""

import json
import os
from collections import Counter


def _write_jsonl(path: str, samples: list[dict]):
    """把样本列表写为 jsonl，每行一条，中文不转义"""
    with open(path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")


def write_datasets(
    valid_samples: list[dict],
    rejected_samples: list[dict],
    output_dir: str,
) -> dict:
    """把样本按 split 分组写入 jsonl，并输出 stats.json。"""
    os.makedirs(output_dir, exist_ok=True)

    # 按 split 分组
    by_split = {"train": [], "val": [], "test": []}
    for s in valid_samples:
        split = s["split"]
        if split in by_split:
            by_split[split].append(s)

    # 写入三个 split 文件
    for split, items in by_split.items():
        _write_jsonl(os.path.join(output_dir, f"{split}.jsonl"), items)

    # 写入 rejected.jsonl
    _write_jsonl(os.path.join(output_dir, "rejected.jsonl"), rejected_samples)

    # 统计
    total_valid = len(valid_samples)
    total_rejected = len(rejected_samples)
    pass_rate = (
        round(total_valid / (total_valid + total_rejected) * 100, 2)
        if (total_valid + total_rejected) > 0
        else 0.0
    )

    stats = {
        "total_valid": total_valid,
        "total_rejected": total_rejected,
        "validator_pass_rate": pass_rate,
        "by_split": {k: len(v) for k, v in by_split.items()},
        "by_difficulty": dict(Counter(s["difficulty"] for s in valid_samples)),
        "by_template": dict(Counter(s["template_id"] for s in valid_samples)),
    }

    # 写 stats.json
    with open(os.path.join(output_dir, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    return stats