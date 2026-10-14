"""
Phase 0 数据流水线编排器：加载配置 → 生成 prompt → 调 teacher → 校验 → 写出数据集。
"""

import os
import sys

from src.prompt_generator import generate_samples, load_topics
from src.teacher_caller import call_teacher
from src.validator import validate_response
from src.dataset_writer import write_datasets

from config.constraint_spec import CONSTRAINT_SPEC, DIFFICULTY_COMPOSITION
from config.template_registry import TEMPLATE_REGISTRY


def run_pipeline(
    output_dir: str = "data",
    n_per_family: int = 40,
    seed: int = 42,
    limit: int = None,
    teacher_model: str = "qwen3.8:27b",
    teacher_base_url: str = "http://localhost:11434/v1",
    teacher_api_key: str = "ollama",
    topics_path: str = "data/topics.json",
) -> dict:
    """跑完整的 Phase 0 数据流水线。"""

    # ============ 步骤 1：加载配置 ============
    print("[1/4] 加载配置...")
    topics = load_topics(topics_path)
    print(f"      模板族: {len(TEMPLATE_REGISTRY)} 个")
    print(f"      主题域: {len(topics)} 个")

    # ============ 步骤 2：生成候选样本 ============
    print("[2/4] 生成候选 prompt...")
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=topics,
        n_per_family=n_per_family,
        seed=seed,
    )
    if limit is not None:
        samples = samples[:limit]
    print(f"      生成 {len(samples)} 条候选样本")

    # ============ 步骤 3：调 teacher + 校验 ============
    print("[3/4] 调用 Teacher 并校验...")
    valid_samples = []
    rejected_samples = []

    for i, sample in enumerate(samples, 1):
        print(f"      [{i}/{len(samples)}] {sample['id']} ...", end=" ", flush=True)

        result = call_teacher(
            prompt=sample["prompt"],
            model=teacher_model,
            base_url=teacher_base_url,
            api_key=teacher_api_key,
        )

        # Teacher 调用失败 → 直接进 rejected
        if result["error"]:
            rejected_samples.append({
                **sample,
                "response": "",
                "violations": [f"teacher_error: {result['error']}"],
            })
            print(f"❌ teacher 失败")
            continue

        # 校验
        passed, violations = validate_response(result["response"], sample["constraints"])

        if passed:
            valid_samples.append({**sample, "response": result["response"]})
            print("✅")
        else:
            rejected_samples.append({
                **sample,
                "response": result["response"],
                "violations": violations,
            })
            print(f"❌ {len(violations)} 项违规")

    # ============ 步骤 4：写出数据集 ============
    print("[4/4] 写出数据集...")
    stats = write_datasets(valid_samples, rejected_samples, output_dir)

    print(f"\n完成！")
    print(f"  通过: {stats['total_valid']}")
    print(f"  拒绝: {stats['total_rejected']}")
    print(f"  通过率: {stats['validator_pass_rate']}%")

    return stats