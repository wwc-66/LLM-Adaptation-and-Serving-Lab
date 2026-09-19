"""
响应校验器：根据结构化 constraints 判定模型回答是否合格。
返回 (passed: bool, violations: list[str])。
"""

import re

def validate_response(response: str, constraints: dict) -> tuple[bool, list[str]]:
    """
    校验 response 是否满足所有 constraints。
    支持的约束类型：
      - length: {"min": int, "max": int}
      - paragraph: {"num_paragraphs": int, "sentences_per_paragraph": int}
      - forbidden_word: [str, str, ...]
    """
    violations = []

    # 1.长度约束
    if "length" in constraints:
        # 获取合规长度范围
        cfg = constraints["length"]
        # 读取response文本长度
        n = len(response)
        # 检验长度是否合规，如否，返回错误信息
        if n < cfg["min"] or n > cfg["max"]:
            violations.append(f"长度 {n} 不在 [{cfg['min']}, {cfg['max']}] 范围内")

    # 2.段落约束
    if "paragraph" in constraints:
        cfg = constraints["paragraph"]
        # 优先按空行切分（\n 后跟任意空白再跟 \n）
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', response) if p.strip()]
        # 如果只切出一段，但文本里有单换行，退化为单换行切分
        if len(paragraphs) == 1 and '\n' in response:
            paragraphs = [p.strip() for p in response.split('\n') if p.strip()]

        # 检验段落数是否合规
        if len(paragraphs) != cfg["num_paragraphs"]:
            violations.append(f"段落数 {len(paragraphs)} 不等于 {cfg['num_paragraphs']}")

        else:
            # 段数正确则逐段检查句数
            for i, para in enumerate(paragraphs):
                # 按句末标点切分，过滤空串
                sentences = [s for s in re.split(r'[。！？]', para) if s.strip()]
                if len(sentences) != cfg["sentences_per_paragraph"]:
                    violations.append(
                        f"第 {i+1} 段句数 {len(sentences)} 不等于 {cfg['sentences_per_paragraph']}"
                        )

    # 3.禁用词约束
    # 检查 response 中是否包含 constraints 中的禁用词
    if "forbidden_word" in constraints:
        for word in constraints["forbidden_word"]:
            #包含禁用词，返回错误信息
            if word in response:
                violations.append(f"出现禁用词 '{word}'")

    #返回错误信息列表，若为空则表示校验通过
    return (len(violations) == 0, violations)