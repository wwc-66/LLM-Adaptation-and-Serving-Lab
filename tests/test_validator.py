# tests/test_validator.py
import pytest
from src.validator import validate_response


def make_long_text(n: int) -> str:
    """生成恰好 n 个字符的字符串（用于长度测试）"""
    return "字" * n


def make_paragraphs(num_paragraphs: int, sentences_per_paragraph: int) -> str:
    """生成符合段落约束的文本"""
    paragraph = "这是一句话。" * sentences_per_paragraph
    return "\n\n".join([paragraph] * num_paragraphs)

def make_sentence(char_count: int = 6, ending: str = "。") -> str:
    """
    生成一句，总字符数 = char_count（含结尾标点）
    默认：6 字 + "。" = 6 字符
    """
    return "字" * (char_count - 1) + ending


def make_paragraph(num_sentences: int, chars_per_sentence: int = 6) -> str:
    """生成一段，内含 num_sentences 句，每句 chars_per_sentence 字符"""
    return "".join([make_sentence(chars_per_sentence) for _ in range(num_sentences)])


def make_paragraphs(num_paragraphs: int, num_sentences: int, chars_per_sentence: int = 6) -> str:
    """
    生成 num_paragraphs 段，每段 num_sentences 句，每句 chars_per_sentence 字符。
    段落间用两个换行分隔，段内句子直接相邻。
    """
    paragraph = make_paragraph(num_sentences, chars_per_sentence)
    return "\n\n".join([paragraph] * num_paragraphs)

"""
def test_xxx():
    # 1. 准备输入
    response = ...          # 待检查的文本
    constraints = {...}     # 约束条件
    
    # 2. 调用被测试的函数（此时还不存在，所以会报错，这是正常的）
    passed, violations = validate_response(response, constraints)
    
    # 3. 断言预期
    assert passed is True/False
    # 可选：assert violations 包含特定内容
"""


# ============ A 组：长度 ============
def test_length_exact_min():
    """边界下限80字"""
    response = make_long_text(80)
    constraints = {"length": {"min": 80, "max": 100}}
    passed, _ = validate_response(response, constraints)
    assert passed is True

def test_length_below_min():
    """低于下限79字，判False"""
    response = make_long_text(79)
    constraints = {"length": {"min": 80, "max": 100}}
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

def test_length_exact_max():
    """边界上限100字"""
    response = make_long_text(100)
    constraints = {"length": {"min": 80, "max": 100}}
    passed, _ = validate_response(response, constraints)
    assert passed is True

def test_length_above_max():
    """高于上限101字，判False"""
    response = make_long_text(101)
    constraints = {"length": {"min": 80, "max": 100}}
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

def test_length_within_range():
    """90字中间值，判True"""
    response = make_long_text(90)
    constraints = {"length": {"min": 80, "max": 100}}
    passed, _ = validate_response(response, constraints)
    assert passed is True

# =========== B 组：段落 ============
def test_paragraphs_exact():
    """标准：3段，每段2句"""
    response = make_paragraphs(3, 2)
    constraints = {"paragraph": {"num_paragraphs": 3, "sentences_per_paragraph": 2}}
    passed, _ = validate_response(response, constraints)
    assert passed is True

def test_paragraphs_less_sentences():
    """段数正确，句数仅为1"""
    response = make_paragraphs(3, 1)
    constraints = {"paragraph": {"num_paragraphs": 3, "sentences_per_paragraph": 2}}
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

def test_paragraphs_less_paragraphs():
    """段数仅为2，句数正确"""
    response = make_paragraphs(2, 2)
    constraints = {"paragraph": {"num_paragraphs": 3, "sentences_per_paragraph": 2}}
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

def test_paragraphs_more_paragraphs():
    """段数为4，句数正确"""
    response = make_paragraphs(4, 2)
    constraints = {"paragraph": {"num_paragraphs": 3, "sentences_per_paragraph": 2}}
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

def test_paragraphs_less_particular_sentence():
    """段数正确，但某段句数不符"""
    response = "这是一句话。\n\n这是一句话。\n\n这是一句话。这是一句话。"
    constraints = {"paragraph": {"num_paragraphs": 3, "sentences_per_paragraph": 2}}
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

# ============ C 组：禁用词 ============
def test_forbidden_word_valid():
    """完全不含禁用词"""
    response = "文本"
    constraints = {"forbidden_word": ["因此", "所以"]}
    passed, _ = validate_response(response, constraints)
    assert passed is True

def test_forbidden_word_invalid_one():
    """含有一个禁用词"""
    response = "文本+因此"
    constraints = {"forbidden_word": ["因此", "所以"]}
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

def test_forbidden_word_invalid_multiple():
    """含有多个禁用词"""
    response = "文本+因此+所以"
    constraints = {"forbidden_word": ["因此", "所以"]}
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

def test_forbidden_word_no_forbidden():
    """禁用词列表为空"""
    response = "文本"
    constraints = {"forbidden_word": []}
    passed, _ = validate_response(response, constraints)
    assert passed is True

# ============ D 组：组合约束 ============
def test_combined_constraints_valid():
    """长度+段落都满足"""
    response = make_paragraphs(3, 2, chars_per_sentence=20)
    constraints = {"length": {"min": 80, "max": 200},
                   "paragraph": {"num_paragraphs": 3, "sentences_per_paragraph": 2}}
    passed, _ = validate_response(response, constraints)
    assert passed is True

def test_combined_constraints_invalid_paragraph():
    """长度满足，但段落不满足"""
    response = make_paragraphs(2, 2, chars_per_sentence=40)
    constraints = {"length": {"min": 80, "max": 200},
                   "paragraph": {"num_paragraphs": 3, "sentences_per_paragraph": 2}}
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

def test_combined_constraints_all():
    """长度、段落数、禁用词全部满足"""
    response = make_paragraphs(3, 2, chars_per_sentence=20)
    constraints = {
        "length": {"min": 80, "max": 200},
        "paragraph": {"num_paragraphs": 3, "sentences_per_paragraph": 2},
        "forbidden_word": ["因此", "所以"]
    }
    passed, _ = validate_response(response, constraints)
    assert passed is True

def test_combined_constraints_forbidden_word_invalid():
    """长度、段落数满足，但含有禁用词"""
    response = make_paragraphs(3, 2, chars_per_sentence=20)
    response = response.replace("字字", "因此", 1)
    constraints = {
        "length": {"min": 80, "max": 200},
        "paragraph": {"num_paragraphs": 3, "sentences_per_paragraph": 2},
        "forbidden_word": ["因此", "所以"]
    }
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

# =========== E 组：边界与异常 ============
def test_empty_response():
    """空文本"""
    response = ""
    constraints = {"length": {"min": 80, "max": 100}}
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

def test_empty_words():
    """空白字符"""
    response = "\n\n"
    constraints = {"length": {"min": 80, "max": 100}}
    passed, violations = validate_response(response, constraints)
    assert passed is False
    assert len(violations) > 0

# ============ F 组：已知限制的回归测试 ============

def test_quote_after_period():
    """
    已知限制：句末标点后带引号，内容会错位，但句数统计正确。
    本测试用于锁定当前行为，未来如果修复，测试需要同步更新。
    """
    response = "妈妈说“我今晚要加班。”然后离开了。\n\n第二段第一句。第二段第二句。\n\n第三段第一句。第三段第二句。"
    constraints = {"paragraph": {"num_paragraphs": 3, "sentences_per_paragraph": 2}}
    passed, _ = validate_response(response, constraints)
    assert passed is True      # 句数统计仍正确


def test_single_newline_as_paragraph_separator():
    """单换行分段的文本应被兜底逻辑正确处理"""
    response = "第一段第一句。第一段第二句。\n第二段第一句。第二段第二句。\n第三段第一句。第三段第二句。"
    constraints = {"paragraph": {"num_paragraphs": 3, "sentences_per_paragraph": 2}}
    passed, _ = validate_response(response, constraints)
    assert passed is True