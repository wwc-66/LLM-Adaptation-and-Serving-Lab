# Project Roadmap

## Phase 0: 数据流水线（当前）
- [√] constraint_spec.py    约束规格
- [√] template_registry.py  模板族
- [√] validator.py          响应校验
- [√] prompt_generator.py   prompt 生成
- [√] teacher_caller.py     Teacher 调用
- [ ] dataset_writer.py     数据集写出
- [ ] pipeline.py           流水线编排

## Phase 1: QLoRA 微调
- [ ] 数据格式转换（chat template）
- [ ] QLoRA 训练脚本
- [ ] Base vs Post 对比

## Phase 2: vLLM 服务化
- [ ] WSL2 环境验证
- [ ] vLLM 部署
- [ ] OpenAI 兼容接口

## Phase 3: 推理优化
- [ ] TTFT / TPOT 基准测试
- [ ] 量化对比
- [ ] 并发压测