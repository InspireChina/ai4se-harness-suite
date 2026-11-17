---
name: tl-arch-plan
description: 编写或更新项目级高阶架构 docs/architecture/（C4、ADR、与业务侧对齐）。当项目准备阶段定技术边界、或跨迭代架构需落盘时使用。
---

# TL：项目级架构设计（Architecture Plan）

在 **项目准备** 或跨迭代演进时，维护 `docs/architecture/` 高阶意图（技术侧为主，业务侧与 BA 协作）。

## 前置

- harness 已铺好（`AGENTS.md`、`docs/`）
- 已读 `docs/standards/architecture.md`、`docs/standards/adr.md`
- 业务侧至少有产品边界草稿（可与 BA 同轮用本 skill 补齐 `business/`）

## 输出位置

| 路径 | 内容 |
|---|---|
| `docs/architecture/README.md` | 索引与分工 |
| `docs/architecture/tech/c4-context.md` | C4 系统上下文 / 集成（PlantUML） |
| `docs/architecture/tech/c4-container.md` | C4 容器（PlantUML） |
| `docs/architecture/tech/adr.md` | 跨迭代 ADR（一张表，每条一句话） |
| `docs/architecture/business/` | 与 BA：glossary / product / core-domain-model（核心+关键字段）/ iterations |

## 硬性约束

- **意图 ≠ as-built**：ADR 与 C4 写目标取舍；实现细节专题仍在 `docs/facts/tech-topic/`
- 核心领域模型（仅核心聚合+关键字段）写 `docs/architecture/business/core-domain-model.md`；全量 as-built 写 `docs/facts/domain-model.md`
- 术语表唯一权威：`docs/architecture/business/glossary.md`
- 迭代级细节写 `docs/features/<迭代>/high-level-design.md`，不要塞进 C4
- 新 ADR：在 `docs/architecture/tech/adr.md` 表追加一行一句话；按 `docs/standards/adr.md`
- 路径不要写死成某台机器的绝对路径

## 与其它 skill

| Skill | 关系 |
|---|---|
| `tl-high-level-design` | 继承本目录 ADR/C4；写本迭 HLD |
| `tl-arch-sync-back` | 实现漂移后对齐技术侧 |
| `ba-arch-sync-back` | 业务侧术语/领域/产品对齐 |
| `ba-write-spec` | 术语写入 `docs/architecture/business/glossary.md` |

## 自检

- [ ] C4 两图可读，外部系统与容器职责清楚
- [ ] 已接受 ADR 有索引；与 `docs/standards` 无冲突
- [ ] business 侧有 glossary 或 product 边界；iterations 指向真实迭代目录
- [ ] 已提示：进迭代前 architecture 须可读
