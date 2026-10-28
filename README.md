# LLM Adaptation & Serving Lab

## Research Question
Can lightweight SFT improve an 8B LLM's compliance with explicit textual constraints 
without degrading its basic response quality?

## 项目结构
- `config/`: 约束规格 + 模板族注册表
- `src/`: 数据生成、校验、训练、Serving 流水线
- `data/`: 训练/验证/测试数据集
- `tests/`: 单元测试（Validator 自测等）

## Phase
- Phase 0: 数据流水线
- Phase 1: QLoRA 微调
- Phase 2: vLLM Serving
- Phase 3: 推理基准测试
- Phase 4: 推理优化

## 环境
- Windows + WSL2 Ubuntu
- RTX 5090 32GB
- Python 3.11

## 数据集规模
- 基于 DeepSeek-V4.1-Flash 作为 Teacher Model 自动生成数据集
- 进行了两轮微调：第一轮 560 条（Teacher 通过率 70%），第二轮扩充至 1120 条（Teacher 通过率 68.48%）

## 微调方法
- 硬件环境：WSL2 + RTX 5090 32GB
- 微调框架：QLoRA (4-bit NormalFloat 量化) + PEFT
- 核心参数：LoRA rank (r=8), lora_alpha=16, target_modules=q/k/v/o_proj, 8 Epochs
- Loss 收敛：从 2.52 稳步降至 0.64（最终训练 loss）

## 实验对比
### 实验对比
| 模型阶段 | 测试集通过率 | Simple | Medium | Hard |
| :--- | :--- | :--- | :--- | :--- |
| Base Qwen3-8B (Zero-shot) | 7.5% | 14.7% | 0.0% | 10.0% |
| Fine-tuned (560条) | 26.25% | 26.5% | 30.6% | 10.0% |
| Fine-tuned (1120条) | 37.66% | 37.3% | 44.4% | 17.4% |
| + 工程后处理截断 | 39.38% | 42.4% | 38.5% | 31.3% |

## 结论
1. **SFT 有效性**：QLoRA 显著提升了小参数模型（8B）对长指令和多约束的遵循能力，整体通过率相对提升超 400%。
2. **Format Drift (格式漂移)**：模型在训练集（长指令）上表现良好，但在测试集（极简短指令）上出现严重的排版遗忘（缺失换行）。证明 SFT 依赖上下文，缺乏分布外 (OOD) 泛化能力，这是 Base 模型预训练偏好导致的边界。
3. **算法与工程互补**：算法微调解决了“内容层面”的生成，而针对 Token 边界的字符数抖动，必须引入系统工程（后处理截断/正则）才能达到可用的商业指标