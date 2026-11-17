# 架构决策记录（ADR）规范

> 本文约定 **如何写 ADR**。已接受的决策正文落在 `docs/facts/tech-topic/`（as-built），不写在本目录。

## 1. 何时写 ADR

满足任一条件时应写 ADR：

- 跨多个 feature / 迭代仍长期有效的技术取舍（框架、分层、鉴权、主键策略等）
- 迭代高阶设计（`high-level-design.md`）中明确要求沉淀的决策
- 推翻或替换既有 ADR（新建一条，旧条标为已废弃并互链）

**不要**为单 feature 的实现细节写 ADR——那些写在 feature `plan.md`。

## 2. 与 HLD / Plan 的关系

| 文档 | 粒度 | 寿命 |
|---|---|---|
| `docs/features/<迭代>/high-level-design.md` | 本迭代技术边界与跨模块契约 | 迭代内；确认后指导 Plan |
| feature `plan.md` / `_chores/` | 单需求实现方案 | 定稿不改；二次改造新建 |
| `docs/facts/tech-topic/NNN-*.md` | 跨迭代架构决策 | 长期；状态可变 |

流程：HLD 确认 → 写 Plan → 实现；跨迭代取舍按本规范写入 / 更新 ADR。

## 3. 编号与文件名

- 文件名：`NNN-slug.md`（三位序号 + 短横线 slug），例如 `006-redis-session.md`
- 序号在 `docs/facts/tech-topic/` 内递增；不要复用已废弃编号
- 标题：`# ADR-NNN: <一句话决策>`

## 4. 状态

| 状态 | 含义 |
|---|---|
| 提议 | 讨论中，未作为实现依据 |
| 已接受 | 实现与评审以此为准 |
| 已废弃 | 被更新决策取代；文内注明替代 ADR |

## 5. 必含章节

以 [`templates/adr.md`](./templates/adr.md) 为准：

1. 状态 / 日期
2. 上下文
3. 决策
4. 备选方案（含否决原因）
5. 后果（正面 / 负面）

## 6. 落盘与索引

- 正文路径：`docs/facts/tech-topic/NNN-slug.md`
- 写法与模板：本文件 + `templates/adr.md`
- 实现专题（非决策）可同目录共存（如 `error-code.md`），但不要冒充 ADR 编号
