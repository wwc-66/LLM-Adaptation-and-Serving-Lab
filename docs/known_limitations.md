# Known Limitations

## 1. 约束难度分级采用"固定顺序递增"（V1 技术债）

**现状**：
- simple  → 仅 length
- medium  → length + paragraph
- hard    → length + paragraph + forbidden_word

**问题**：
- 单约束场景只覆盖了 length，未覆盖"仅段落"和"仅禁用词"。
- 模型可能学到伪相关："段落约束总与长度约束同现"。

**改进方向（V2）**：
- 难度 = 约束数量。
- simple = 1 类（3 种组合）；medium = 2 类（3 种组合）；hard = 3 类。
- 覆盖全部约束组合，避免伪相关。

**触发时机**：V1 全链路跑通、Baseline 记录后。