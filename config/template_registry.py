"""
模板族注册表：定义"用户可以用哪些措辞表达同一组约束"。
关键：每个模板族的 split 在注册时就固定，绝不跨集合。
占位符说明：
  {length_min}, {length_max}            - 字数范围
  {num_paragraphs}                       - 段落数
  {sentences_per_paragraph}              - 每段句子数
  {forbidden_words}                      - 禁用词（会以 "、" 分隔）
"""

TEMPLATE_REGISTRY = {
    # ==================== TRAIN ====================
    "T1": {
        "split": "train",
        "style": "direct_command",
        "paraphrases": [
            "请用{length_min}~{length_max}字回答，分成{num_paragraphs}段，每段{sentences_per_paragraph}句话，禁止出现{forbidden_words}。",
            "回答要求：字数{length_min}~{length_max}字，分为{num_paragraphs}段，每段{sentences_per_paragraph}句，不得使用{forbidden_words}。",
        ],
    },
    "T2": {
        "split": "train",
        "style": "bullet_list",
        "paraphrases": [
            "回答要求：\n1. 字数{length_min}~{length_max}字\n2. {num_paragraphs}个自然段\n3. 每段{sentences_per_paragraph}句话\n4. 禁止使用{forbidden_words}",
            "请遵守以下规范：\n- {length_min}~{length_max}字\n- {num_paragraphs}段\n- 每段{sentences_per_paragraph}句\n- 禁用词：{forbidden_words}",
        ],
    },
    "T3": {
        "split": "train",
        "style": "casual",
        "paraphrases": [
            "别写太长，{length_min}~{length_max}字就行，分{num_paragraphs}段写，每段{sentences_per_paragraph}句话，另外别用{forbidden_words}这些词。",
            "大概{length_min}到{length_max}字吧，写{num_paragraphs}段，一段{sentences_per_paragraph}句，{forbidden_words}不能用哦。",
        ],
    },
    "T4": {
        "split": "train",
        "style": "role_play",
        "paraphrases": [
            "你现在是一位严谨的科普编辑。请完成下面的写作任务：\n- 字数：{length_min}~{length_max}\n- 结构：{num_paragraphs}段，每段{sentences_per_paragraph}句\n- 禁用词：{forbidden_words}",
            "作为资深内容创作者，请按下述要求作答：字数{length_min}~{length_max}，{num_paragraphs}段，每段{sentences_per_paragraph}句，避免出现{forbidden_words}。",
        ],
    },
    "T5": {
        "split": "train",
        "style": "question_guided",
        "paraphrases": [
            "能否帮我写一段{length_min}~{length_max}字的回答？请分{num_paragraphs}段，每段{sentences_per_paragraph}句。对了，{forbidden_words}这些词不能用。",
            "可以回答一下吗？字数控制在{length_min}~{length_max}，{num_paragraphs}段，每段{sentences_per_paragraph}句，{forbidden_words}不要出现。",
        ],
    },
    "T6": {
        "split": "train",
        "style": "layered_explain",
        "paraphrases": [
            "首先明确字数要求：{length_min}~{length_max}字。其次确定结构：{num_paragraphs}段，每段{sentences_per_paragraph}句。最后注意禁用词：{forbidden_words}。请按此作答。",
            "写作规范如下——字数方面{length_min}~{length_max}字；结构方面{num_paragraphs}段每段{sentences_per_paragraph}句；内容方面不能出现{forbidden_words}。",
        ],
    },
    "T7": {
        "split": "train",
        "style": "scenario_embedded",
        "paraphrases": [
            "我在准备一份材料，需要一段{length_min}~{length_max}字的说明。请分{num_paragraphs}段写，每段{sentences_per_paragraph}句。另外，材料里不希望出现{forbidden_words}这些词。",
            "帮我整理一段文字用于报告：{length_min}~{length_max}字，{num_paragraphs}段，每段{sentences_per_paragraph}句，{forbidden_words}都不要出现。",
        ],
    },
    "T8": {
        "split": "train",
        "style": "polite_request",
        "paraphrases": [
            "麻烦你帮我写一段回答，字数{length_min}~{length_max}字，分成{num_paragraphs}段，每段{sentences_per_paragraph}句。另外，请避免使用{forbidden_words}。",
            "能否请你按以下要求回答：{length_min}~{length_max}字，{num_paragraphs}段，每段{sentences_per_paragraph}句，尽量不要出现{forbidden_words}。",
        ],
    },
    
    # ==================== VALIDATION ====================
    "T9": {
        "split": "val",
        "style": "checklist",
        "paraphrases": [
            "请按检查清单输出：\n[ ] 字数{length_min}~{length_max}\n[ ] {num_paragraphs}段\n[ ] 每段{sentences_per_paragraph}句\n[ ] 无{forbidden_words}",
            "输出前请确认满足：①{length_min}~{length_max}字 ②{num_paragraphs}段 ③每段{sentences_per_paragraph}句 ④不含{forbidden_words}",
        ],
    },
    "T10": {
        "split": "val",
        "style": "contrast_limited",
        "paraphrases": [
            "请注意：不是随便写，而是必须{length_min}~{length_max}字、{num_paragraphs}段、每段{sentences_per_paragraph}句，且不得出现{forbidden_words}。",
            "以下要求全部为硬性：{length_min}~{length_max}字；{num_paragraphs}段；每段{sentences_per_paragraph}句；禁用{forbidden_words}。",
        ],
    },
    "T11": {
        "split": "val",
        "style": "academic",
        "paraphrases": [
            "请依据以下规格生成回答：字符数范围[{length_min}, {length_max}]；段落数={num_paragraphs}；每段句数={sentences_per_paragraph}；禁用词集合={forbidden_words}。",
            "生成约束如下：len∈[{length_min},{length_max}]，para={num_paragraphs}，sent/para={sentences_per_paragraph}，禁止词={forbidden_words}。",
        ],
    },
    
    # ==================== TEST（措辞全新，训练中未出现） ====================
    "T12": {
        "split": "test",
        "style": "terse_declaration",
        "paraphrases": [
            "{length_min}-{length_max}字。{num_paragraphs}段。每段{sentences_per_paragraph}句。禁用：{forbidden_words}。",
            "硬约束｜长度{length_min}~{length_max}｜段落{num_paragraphs}｜句/段{sentences_per_paragraph}｜禁词{forbidden_words}",
        ],
    },
    "T13": {
        "split": "test",
        "style": "progressive",
        "paraphrases": [
            "写一段话。长度：{length_min}~{length_max}字。在此基础上，分{num_paragraphs}段。进一步地，每段{sentences_per_paragraph}句。最后，{forbidden_words}绝对不能出现。",
            "先满足字数{length_min}~{length_max}，再分{num_paragraphs}段，每段{sentences_per_paragraph}句，同时{forbidden_words}不能用。",
        ],
    },
    "T14": {
        "split": "test",
        "style": "dialogic",
        "paraphrases": [
            "问：字数多少？答：{length_min}~{length_max}。问：分几段？答：{num_paragraphs}段，每段{sentences_per_paragraph}句。问：有什么词不能用？答：{forbidden_words}。",
            "字数？{length_min}~{length_max}。段数？{num_paragraphs}。句/段？{sentences_per_paragraph}。禁词？{forbidden_words}。",
        ],
    },
}