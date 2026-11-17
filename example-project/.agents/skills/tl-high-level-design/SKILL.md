---
name: tl-high-level-design
description: 为当前迭代编写高阶技术设计（HLD / TRD）到 docs/features/<迭代>/high-level-design.md，等待人工确认。当迭代规格齐备、进入 feature Plan 之前需要定技术边界与跨模块契约时使用。
---

# TL：迭代高阶技术设计

为 **整个迭代** 写技术边界与跨模块契约（HLD / TRD），不是单个 feature 的实现 Plan。

## 前置

- 本迭代各 feature 的 `spec.md` 已齐备（或至少范围稳定）
- 已读 `docs/standards/architecture.md`、`docs/standards/adr.md`
- 已扫过 `docs/facts/tech-topic/` 既有 ADR，避免重复或冲突决策

## 输出位置

`docs/features/<迭代>/high-level-design.md`

示例：`docs/features/iteration1/high-level-design.md`

## 文档结构（最低要求）

1. 背景与目标 / 非目标
2. 本迭代范围（feature 索引表）
3. 技术边界（栈、部署、继承的 ADR）
4. 跨模块契约（提供方 / 消费方 / 权属）
5. 开放决策（确认前应关闭或延期）
6. 确认清单（含 **人工确认** 闸门）
7. AI 实现提示

## 硬性约束

- **等人确认**：状态未变为已确认前，禁止对该迭代执行 `dev-plan` 写实现方案或编码
- 可与 `qa-write-cases` **并行**（规格确认后即可写 QA 用例）
- 不要把单 feature 的表结构 / API 细节写进 HLD——那些属于 feature `plan.md`
- 跨迭代长期取舍按 `docs/standards/adr.md` 撰写，接受后落到 `docs/facts/tech-topic/NNN-slug.md`
- 路径不要写死成某个机器的绝对路径

## 与 Plan / ADR 的关系

| 文档 | 谁写 | 何时 |
|---|---|---|
| `high-level-design.md` | TL（本 skill） | 迭代前；确认后才开 Plan |
| feature `plan.md` / `_chores/` | DEV（`dev-plan`） | HLD 已确认 |
| `docs/facts/tech-topic/NNN-*.md` | TL / 架构 | 跨迭代决策接受后 |

## 自检

- [ ] 文件在正确的迭代目录，且迭代 README 已挂索引
- [ ] 跨模块契约无双头所有
- [ ] 与既有 ADR 无未解释冲突
- [ ] 开放决策已关闭或标明不影响开工顺序
- [ ] 已提示用户确认；未确认不进入 `dev-plan`
