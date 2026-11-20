---
name: tl-arch-plan
description: 编写或更新项目级高阶架构的技术侧 docs/architecture/tech/（C4 上下文/容器、ADR）。当项目准备阶段业务边界已定、需要切技术边界时使用。
---

# TL：项目级架构设计（Architecture Plan）

在 **项目准备** 或跨迭代演进时，维护 `docs/architecture/tech/`：C4 上下文/容器与跨迭代 ADR。
业务侧（product / glossary / core-domain-model / iterations）是 `ba-arch-plan` 的产出，本 skill 只读。

## 前置

- harness 已铺好（`AGENTS.md`、`docs/`）
- 已读 `docs/standards/architecture.md`、`docs/standards/adr.md`
- **业务边界已定**：`docs/architecture/business/` 至少有 product 一句话与核心聚合；
  没有就先用 `ba-arch-plan`（先画图再定边界，图必重画）

## 输出位置

| 路径 | 内容 |
|---|---|
| `docs/architecture/README.md` | 索引与分工（与 `ba-arch-plan` 共同维护） |
| `docs/architecture/tech/c4-context.md` | C4 系统上下文 / 集成（PlantUML） |
| `docs/architecture/tech/c4-container.md` | C4 容器（PlantUML） |
| `docs/architecture/tech/adr.md` | 跨迭代 ADR（一张表，每条一句话） |

**不输出** `business/` 正文 —— 那是 `ba-arch-plan` 的落点；本文只读它来做切分依据。

## 硬性约束

- **意图 ≠ as-built**：ADR 与 C4 写目标取舍；实现细节专题仍在 `docs/facts/tech-topic/`
- **容器必须能承载核心聚合**；切分依据是 `docs/architecture/business/core-domain-model.md` 的核心聚合 + 关键字段，不是代码目录
- 核心领域模型（仅核心聚合+关键字段）在 `docs/architecture/business/core-domain-model.md`；全量 as-built 在 `docs/facts/domain-model.md`
- 术语表唯一权威：`docs/architecture/business/glossary.md`
- 迭代级细节写 `docs/features/<迭代>/high-level-design.md`，不要塞进 C4
- 新 ADR：在 `docs/architecture/tech/adr.md` 表追加一行一句话；按 `docs/standards/adr.md`
- 路径不要写死成某台机器的绝对路径

## 与其它 skill

| Skill | 关系 |
|---|---|
| `ba-arch-plan` | 前置：业务边界、术语、核心聚合由它起草；本 skill 读它做切分 |
| `tl-high-level-design` | 继承本目录 ADR/C4；写本迭 HLD |
| `tl-arch-sync-back` | 实现漂移后对齐技术侧 |
| `ba-arch-sync-back` | 业务侧术语/领域/产品对齐 |
| `ba-write-spec` | 术语写入 `docs/architecture/business/glossary.md` |

## 自检

- [ ] C4 两图可读，外部系统与容器职责清楚
- [ ] 每个容器能说清承载哪些核心聚合（能对上 `docs/architecture/business/core-domain-model.md`）
- [ ] 已接受 ADR 有索引；与 `docs/standards` 无冲突
- [ ] 没有往 `business/` 里写正文（那是 `ba-arch-plan` 的活）
- [ ] `docs/architecture/README.md` 的技术侧链接可点、业务侧条目存在
- [ ] 已提示：进迭代前 architecture 须可读
