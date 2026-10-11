import pytest
from src.prompt_generator import generate_samples

from config.template_registry import TEMPLATE_REGISTRY
from config.constraint_spec import CONSTRAINT_SPEC, DIFFICULTY_COMPOSITION


# 测试用的小型 topics
TEST_TOPICS = {
    "science": ["为什么天空是蓝色的", "彩虹是怎么形成的"],
    "history": ["丝绸之路的历史意义", "秦始皇统一六国的影响"],
}


# ============ A 组：结构验证 ============

def test_returns_list():
    """返回类型是 list"""
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    assert isinstance(samples, list)


def test_sample_has_required_fields():
    """每条样本必须包含必需字段"""
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    required = {"id", "template_id", "split", "style", "topic",
                "topic_domain", "difficulty", "constraints", "prompt"}
    for s in samples:
        assert required.issubset(s.keys())


def test_ids_are_unique():
    """所有样本 id 不重复"""
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    ids = [s["id"] for s in samples]
    assert len(ids) == len(set(ids))


# ============ B 组：难度与约束映射 ============

def test_simple_samples_have_only_length():
    """simple 难度样本只含 length 约束"""
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    for s in samples:
        if s["difficulty"] == "simple":
            assert list(s["constraints"].keys()) == ["length"]


def test_medium_samples_have_length_and_paragraph():
    """medium 难度样本含 length + paragraph"""
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    for s in samples:
        if s["difficulty"] == "medium":
            assert set(s["constraints"].keys()) == {"length", "paragraph"}


def test_hard_samples_have_all_three():
    """hard 难度样本含全部三类约束"""
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    for s in samples:
        if s["difficulty"] == "hard":
            assert set(s["constraints"].keys()) == {"length", "paragraph", "forbidden_word"}

# ============ C 组：Split 一致性 ============

def test_split_matches_registry():
    """样本的 split 字段与 template_registry 里对应族的 split 一致"""
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    for s in samples:
        expected_split = TEMPLATE_REGISTRY[s["template_id"]]["split"]
        assert s["split"] == expected_split


def test_all_three_splits_are_produced():
    """输出里必须同时存在 train / val / test 三种 split"""
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    splits = {s["split"] for s in samples}
    assert splits == {"train", "val", "test"}


# ============ D 组：prompt 生成质量 ============

def test_no_unfilled_placeholders():
    """prompt 里不能残留 {xxx} 形式的占位符"""
    import re
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    for s in samples:
        leftovers = re.findall(r"\{[a-zA-Z_]+\}", s["prompt"])
        assert leftovers == [], f"未填充占位符: {leftovers} 在 {s['id']} 中"


def test_prompt_contains_topic():
    """prompt 里必须包含对应的 topic 文本"""
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    for s in samples:
        assert s["topic"] in s["prompt"]


def test_prompt_contains_constraint_values():
    """prompt 里必须出现 constraints 中所有关键数值"""
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    for s in samples:
        constraints = s["constraints"]
        prompt = s["prompt"]
        if "length" in constraints:
            assert str(constraints["length"]["min"]) in prompt
            assert str(constraints["length"]["max"]) in prompt
        if "paragraph" in constraints:
            assert str(constraints["paragraph"]["num_paragraphs"]) in prompt
            assert str(constraints["paragraph"]["sentences_per_paragraph"]) in prompt
        if "forbidden_word" in constraints:
            for w in constraints["forbidden_word"]:
                assert w in prompt


# ============ E 组：可复现性 ============

def test_same_seed_produces_identical_output():
    """相同 seed 两次生成完全一致"""
    kwargs = dict(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    a = generate_samples(**kwargs)
    b = generate_samples(**kwargs)
    assert a == b


def test_different_seed_produces_different_output():
    """不同 seed 生成内容有差异"""
    kwargs = dict(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
    )
    a = generate_samples(seed=42, **kwargs)
    b = generate_samples(seed=43, **kwargs)
    # 至少有一条样本不一样
    assert a != b


# ============ F 组：分布控制 ============

def test_total_sample_count():
    """总条数 = 14 族 × n_per_family"""
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=10,
        seed=42,
    )
    assert len(samples) == 14 * 10


def test_difficulty_distribution_respected():
    """每族的难度分布严格等于 difficulty_dist 换算的整数"""
    difficulty_dist = {"simple": 0.3, "medium": 0.5, "hard": 0.2}
    n_per_family = 10
    samples = generate_samples(
        template_registry=TEMPLATE_REGISTRY,
        constraint_spec=CONSTRAINT_SPEC,
        difficulty_composition=DIFFICULTY_COMPOSITION,
        topics=TEST_TOPICS,
        n_per_family=n_per_family,
        difficulty_dist=difficulty_dist,
        seed=42,
    )
    # 按族分组统计
    from collections import defaultdict
    family_counts = defaultdict(lambda: {"simple": 0, "medium": 0, "hard": 0})
    for s in samples:
        family_counts[s["template_id"]][s["difficulty"]] += 1

    # 期望分布：10 × 0.3 = 3, 10 × 0.5 = 5, 10 × 0.2 = 2
    expected = {
        "simple": round(n_per_family * difficulty_dist["simple"]),
        "medium": round(n_per_family * difficulty_dist["medium"]),
        "hard":   round(n_per_family * difficulty_dist["hard"]),
    }
    for tid, counts in family_counts.items():
        assert counts == expected, f"{tid} 分布 {counts} 不等于期望 {expected}"