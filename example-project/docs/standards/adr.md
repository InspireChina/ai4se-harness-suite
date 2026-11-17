# 架构决策记录（ADR）规范

> 已接受的决策落在 `docs/architecture/tech/adr.md`：**一张表，每条 ADR 一句话**。

## 1. 何时记一条

- 跨多个 feature / 迭代仍长期有效的技术取舍
- 迭代 HLD 中要求沉淀的决策
- 推翻既有决策时：改状态为已废弃，并新增一行替代决策

**不要**为单 feature 实现细节写 ADR——那些写在 feature `plan.md` 或 `facts/tech-topic/`。

## 2. 怎么写

在 `docs/architecture/tech/adr.md` 表格中追加一行：

| 列 | 要求 |
|---|---|
| 编号 | `ADR-NNN`，序号递增，不复用 |
| 决策（一句话） | 一句说清取舍；不要上下文/备选/后果长文 |
| 状态 | 提议 / 已接受 / 已废弃 |

需要展开的实现说明写到 `docs/facts/tech-topic/`，不要把 ADR 表撑成论文。

## 3. 与其它文档

| 文档 | 粒度 |
|---|---|
| `docs/architecture/tech/adr.md` | 项目级一句话决策表 |
| `docs/features/<迭代>/high-level-design.md` | 本迭边界；引用 ADR 编号 |
| feature `plan.md` | 单需求方案 |
| `docs/facts/tech-topic/` | as-built 实现专题 |
