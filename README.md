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