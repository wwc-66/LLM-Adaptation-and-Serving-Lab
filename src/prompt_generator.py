"""
Prompt 生成器：把约束规格 + 模板族 + 主题组合成完整的自然语言 prompt。
"""

import json
import random

# 样本难度 → 单约束难度档的映射
DIFFICULTY_TO_SPEC_KEY = {
    "simple": "loose",
    "medium": "medium",
    "hard": "strict"
}

def load_topics(path: str) -> dict:
    """从 json 文件读取 topics"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _pick_topic(topics:dict, rng: random.Ramdom) -> tuple[str, str]:
    """从 topics 里随机抽一个主题，返回 (topic, domain)"""
    domain = rng.choice(list(topics.keys()))
    topic = rng.choice(topics[domain])
    return topic, domain

def _build_constraints(
        difficulty: str,
        constraint_spec: dict,
        difficulty_composition: dict,
        rng: random.Random
) -> dict:
    """
    根据难度抽取约束值。
    难度决定“用哪几类约束”，约束规格决定“具体数值是多少”。
    """
    spec_key = DIFFICULTY_TO_SPEC_KEY[difficulty]
    constraint_types = difficulty_composition[difficulty]

    constraints = {}
    for ctype in constraint_types:
        constraints[ctype] = rng.choice(constraint_spec[ctype][spec_key])
    return constraints

def _build_prompt(
        template_family: dict,
        topic: str,
        constraints: dict,
        rng: random.Random
) -> str:
    """
    把模板片段渲染成自然语言 prompt。
    每个片段从 paraphrase 列表里随机选一个变体。
    """
    parts = [rng.choice(template_family["intro"]).format(topic=topic)]

    if "length" in constraints:
        parts.append(
            rng.choice(template_family["length"]).format(**constraints["length"])
            )
    if "paragraph" in constraints:
        parts.append(
            rng.choice(template_family["paragraph"]).format(**constraints["paragraph"])
            )
    if "forbidden_word" in constraints:
        words = "、".join(constraints["forbidden_word"])
        parts.append(
            rng.choice(template_family["forbidden"]).format(forbidden_words=words)
            )

    return "\n".join(parts)

def _allocate_difficulties(n: int, difficulty_dist: dict) -> dict:
    """
    按分布精确分配 n 条样本的难度数量。
    用 round 分配前两档，hard 用 n 减去它们，保证总数严格等于 n。
    """
    simple = round(n * difficulty_dist["simple"])
    medium = round(n * difficulty_dist["medium"])
    hard = n - simple - medium
    return {"simple": simple, "medium": medium, "hard": hard}


def generate_samples(
    template_registry: dict,
    constraint_spec: dict,
    difficulty_composition: dict,
    topics: dict,
    n_per_family: int = 40,
    difficulty_dist: dict = None,
    seed: int = 42,
) -> list[dict]:
    if difficulty_dist is None:
        difficulty_dist = {"simple": 0.3, "medium": 0.5, "hard": 0.2}

    rng = random.Random(seed)   # 用独立实例，不污染全局
    samples = []

    for tid, family in template_registry.items():
        split = family["split"]
        style = family["style"]
        alloc = _allocate_difficulties(n_per_family, difficulty_dist)

        counter = 0
        for difficulty in ["simple", "medium", "hard"]:
            for _ in range(alloc[difficulty]):
                counter += 1

                topic, domain = _pick_topic(topics, rng)
                constraints = _build_constraints(
                    difficulty, constraint_spec, difficulty_composition, rng
                )
                prompt = _build_prompt(family, topic, constraints, rng)

                samples.append({
                    "id": f"{split}_{tid}_{counter:04d}",
                    "template_id": tid,
                    "split": split,
                    "style": style,
                    "topic": topic,
                    "topic_domain": domain,
                    "difficulty": difficulty,
                    "constraints": constraints,
                    "prompt": prompt,
                })

    return samples