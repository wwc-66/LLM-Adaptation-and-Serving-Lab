# Phase 0 数据流水线架构

## 数据流

配置层 (constraint_spec.py / template_registry.py / topics.json)
    ↓ 加载
src/prompt_generator.py
    → 输出：list[dict]（每条含 id/split/prompt/constraints/topic）
    ↓ 
src/teacher_caller.py
    → 输入：prompt 字符串
    → 输出：dict{response, attempts, error, latency_ms}
    ↓ 
src/validator.py
    → 输入：(response, constraints)
    → 输出：(passed: bool, violations: list)
    ↓
src/dataset_writer.py
    → 输入：(valid_samples, rejected_samples)
    → 输出：train.jsonl / val.jsonl / test.jsonl / stats.json

## 关键决策

1.split 在 prompt_generator 里赋值，按”模板族“分配，不按”样本“随机切。
    原因：避免模板级数据泄漏。

2.teacher_caller 有重试+指数退避。
    原因：网络/服务端可能短暂失败，重试能提高成功率。

3.validator 在 teacher_caller 之后。
    原因：校验的对象是 response，没有 response 就没得校验。