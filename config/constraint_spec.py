"""
约束规格：定义三类约束的取值空间与难度分级。
Generator 和 Validator 都从这里读取，确保标准一致。
"""

CONSTRAINT_SPEC = {
    "length": {
        "loose": [{"min": 80, "max": 100}],

        "medium": [{"min": 60, "max": 80},
                   {"min": 100, "max": 150}],

        "strict": [{"min": 50, "max": 70},
                 {"min": 150, "max": 200}]
    },

    "paragraph": {
        "loose": [{"num_paragraphs": 2, "sentences_per_paragraph": 2}],

        "medium": [{"num_paragraphs": 3, "sentences_per_paragraph": 2}],

        "strict": [{"num_paragraphs": 4, "sentences_per_paragraph": 3}]
    },

    "forbidden_word": {
        "loose": [["因此"]],

        "medium": [["因此", "所以"],["首先", "其次"]],

        "strict": ["因此", "所以", "从而", "进而"],
    }
}

#难度组合规则：一条样本包含哪几类约束
DIFFICULTY_COMPOSITION = {
    #只含一类
    "simple" :["length"],
    #含两类
    "medium": ["length","paragraph"],
    #三类全含
    "hard": ["length", "paragraph", "forbidden_word"]
}