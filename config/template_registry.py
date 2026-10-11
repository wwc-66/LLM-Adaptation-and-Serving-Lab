"""
模板族注册表：定义"用户可以用哪些措辞表达同一组约束"。
关键：每个模板族的 split 在注册时就固定，绝不跨集合。
占位符说明：
  {min}, {max}            - 字数范围
  {num_paragraphs}                       - 段落数
  {sentences_per_paragraph}              - 每段句子数
  {forbidden_words}                      - 禁用词（会以 "、" 分隔）
"""

TEMPLATE_REGISTRY = {
    # ==================== TRAIN ====================
    "T1": {
        "split": "train",
        "style": "direct_command",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["请回答以下问题：{topic}。",
                       "请就以下问题给出回答：{topic}。"],
        "length":     ["回答控制在{min}~{max}字。",
                       "回答要求：字数{min}~{max}字。"],
        "paragraph":  ["分成{num_paragraphs}段，每段{sentences_per_paragraph}句话。",
                       "分为{num_paragraphs}段，每段{sentences_per_paragraph}句。"],
        "forbidden":  ["禁止出现“{forbidden_words}”。",
                       "不得使用“{forbidden_words}”。"],
    },

    "T2": {
        "split": "train",
        "style": "bullet_list",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["任务：{topic}\n要求如下：",
                       "完成任务：{topic}\n请遵守以下规范："],
        "length":     ["1. 字数{min}~{max}字。",
                       "- {min}~{max}字。"],
        "paragraph":  ["2. {num_paragraphs}个自然段\n3. 每段{sentences_per_paragraph}句话。",
                       "- {num_paragraphs}段\n- 每段{sentences_per_paragraph}句。"],
        "forbidden":  ["4. 禁止使用{forbidden_words}。",
                       "- 禁用词：{forbidden_words}。"],
    },

    "T3": {
        "split": "train",
        "style": "casual",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["帮我讲讲这个问题吧：{topic}。",
                       "我想了解一下：{topic}。"],
        "length":     ["别写太长，{min}~{max}字就行。",
                       "大概{min}到{max}字吧。"],
        "paragraph":  ["分{num_paragraphs}段写，每段{sentences_per_paragraph}句话。",
                       "写{num_paragraphs}段，一段{sentences_per_paragraph}句。"],
        "forbidden":  ["另外别用“{forbidden_words}”这些词。",
                       "“{forbidden_words}”不能用哦。"],
    },

    "T4": {
        "split": "train",
        "style": "role_play",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["你现在是一位严谨的科普编辑。请处理以下主题：{topic}，并完成下面的写作任务：",
                       "作为资深内容创作者，请围绕如下主题{topic}，按下述要求作答："],
        "length":     ["\n- 字数：{min}~{max}。",
                       "字数{min}~{max}。"],
        "paragraph":  ["\n- 结构：{num_paragraphs}段，每段{sentences_per_paragraph}句。",
                       "{num_paragraphs}段，每段{sentences_per_paragraph}句。"],
        "forbidden":  ["\n- 禁用词：“{forbidden_words}”",
                       "避免出现{forbidden_words}。"],
    },

    "T5": {
        "split": "train",
        "style": "question_guided",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["能否帮我讲清楚：{topic}？",
                       "对于这个问题：{topic}，可以回答一下吗？"],
        "length":     ["能否帮我写一段{min}~{max}字的回答？",
                       "字数控制在{min}~{max}。"],
        "paragraph":  ["请分{num_paragraphs}段，每段{sentences_per_paragraph}句。",
                       "{num_paragraphs}段，每段{sentences_per_paragraph}句。"],
        "forbidden":  ["对了，“{forbidden_words}”这些词不能用。",
                       "“{forbidden_words}”不要出现。"],
    },

    "T6": {
        "split": "train",
        "style": "layered_explain",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["为我讲解{topic}，我将分层提出规则说明，请按要求作答。",
                       "讲解一下这个问题：{topic}，并且遵循我提出的多层要求进行回答。"],
        "length":     ["首先明确字数要求：{min}~{max}字。",
                       "写作规范如下——字数方面{min}~{max}字；"],
        "paragraph":  ["其次确定结构：{num_paragraphs}段，每段{sentences_per_paragraph}句。",
                       "结构方面{num_paragraphs}段每段{sentences_per_paragraph}句；"],
        "forbidden":  ["最后注意禁用词：“{forbidden_words}”。请按此作答。",
                       "内容方面不能出现“{forbidden_words}”。"],
    },

    "T7": {
        "split": "train",
        "style": "scenario_embedded",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["我在准备一份关于{topic}的材料，请帮我写。",
                       "有关{topic}这个话题，帮我整理一段文字用于报告："],
        "length":     ["这段说明约{min}~{max}字。",
                       "{min}~{max}字。"],
        "paragraph":  ["请分{num_paragraphs}段写，每段{sentences_per_paragraph}句。",
                       "{num_paragraphs}段，每段{sentences_per_paragraph}句。"],
        "forbidden":  ["另外，材料里不希望出现“{forbidden_words}”这些词。",
                       "{forbidden_words}都不要出现。"],
    },

    "T8": {
        "split": "train",
        "style": "polite_request",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["麻烦你帮我解释一下{topic}，谢谢。",
                       "麻烦你帮我写一段关于“{topic}”这个问题的回答，请按照以下要求："],
        "length":     ["字数限制在{min}~{max}字",
                       "{min}~{max}字"],
        "paragraph":  ["分成{num_paragraphs}段，每段{sentences_per_paragraph}句。",
                       "{num_paragraphs}段，每段{sentences_per_paragraph}句。"],
        "forbidden":  ["另外，请避免使用“{forbidden_words}”。",
                       "尽量不要出现“{forbidden_words}”。"],
    },
    
    # ==================== VALIDATION ====================
    "T9": {
        "split": "val",
        "style": "checklist",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["请按以下检查清单输出关于{topic}的回答：",
                       "回答一下这个问题：{topic}。输出前请确认满足："],
        "length":     ["[ ] 字数{min}~{max}",
                       "①{min}~{max}字 "],
        "paragraph":  ["[ ] {num_paragraphs}段\n[ ] 每段{sentences_per_paragraph}句",
                       "②{num_paragraphs}段 ③每段{sentences_per_paragraph}句 "],
        "forbidden":  ["[ ] 无“{forbidden_words}”",
                       "④不含“{forbidden_words}”。"],
    },

    "T10": {
        "split": "val",
        "style": "contrast_limited",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["请注意，以下要求全部为硬性，主题：{topic}。",
                       "务必遵循以下要求，回答问题：{topic}。"],
        "length":     ["必须{min}~{max}字、",
                       "以下要求全部为硬性：{min}~{max}字；"],
        "paragraph":  ["{num_paragraphs}段、每段{sentences_per_paragraph}句，",
                       "{num_paragraphs}段；每段{sentences_per_paragraph}句；"],
        "forbidden":  ["且不得出现“{forbidden_words}”。",
                       "禁用“{forbidden_words}”。"],
    },

    "T11": {
        "split": "val",
        "style": "academic",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["生成主题：{topic}。规格如下：",
                       "根据主题：{topic}，生成回答，约束如下："],
        "length":     ["字符数范围[{min}, {max}]；",
                       "len∈[{min},{max}]，"],
        "paragraph":  ["段落数={num_paragraphs}；每段句数={sentences_per_paragraph}；",
                       "para={num_paragraphs}，sent/para={sentences_per_paragraph}，"],
        "forbidden":  ["禁用词集合=“{forbidden_words}”。",
                       "禁止词=“{forbidden_words}”。"],
    },
    
    # ==================== TEST（措辞全新，训练中未出现） ====================
    "T12": {
        "split": "test",
        "style": "terse_declaration",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["主题：{topic}",
                       "回答问题：{topic}。"],
        "length":     ["{min}-{max}字。",
                       "硬约束｜长度{min}~{max}｜"],
        "paragraph":  ["{num_paragraphs}段。每段{sentences_per_paragraph}句。",
                       "段落{num_paragraphs}｜句/段{sentences_per_paragraph}｜"],
        "forbidden":  ["禁用：“{forbidden_words}”。",
                       "禁词：“{forbidden_words}”"],
    },

    "T13": {
        "split": "test",
        "style": "progressive",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["请就{topic}作答。要求层层递进：",
                       "围绕{topic}这个话题写一段话，下面是要求："],
        "length":     ["长度：{min}~{max}字。",
                       "先满足字数{min}~{max}，"],
        "paragraph":  ["在此基础上，分{num_paragraphs}段。进一步地，每段{sentences_per_paragraph}句。",
                       "再分{num_paragraphs}段，每段{sentences_per_paragraph}句，"],
        "forbidden":  ["最后，“{forbidden_words}”绝对不能出现。",
                       "同时“{forbidden_words}”不能用。"],
    },

    "T14": {
        "split": "test",
        "style": "dialogic",
        "supported_constraints": ["length", "paragraph", "forbidden_word"],
        "intro":      ["问：请介绍{topic}。答：（请作答）",
                       "解释{topic}？（请作答）"],
        "length":     ["问：字数多少？答：{min}~{max}。",
                       "字数？{min}~{max}。"],
        "paragraph":  ["问：分几段？答：{num_paragraphs}段，每段{sentences_per_paragraph}句。",
                       "段数？{num_paragraphs}。句/段？{sentences_per_paragraph}。"],
        "forbidden":  ["问：有什么词不能用？答：“{forbidden_words}”。",
                       "禁词？“{forbidden_words}”。"],
    },
}