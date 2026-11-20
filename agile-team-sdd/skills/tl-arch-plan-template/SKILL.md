---
name: tl-arch-plan-template
description: 编写或更新项目级高阶架构的技术侧 docs/architecture/tech/（C4 上下文/容器、ADR）。当项目准备阶段业务边界已定、需要切技术边界时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# TL：项目级架构设计（Architecture Plan）

在 **项目准备** 或跨迭代演进时，维护 `{{ARCHITECTURE_DIR}}/tech/`：C4 上下文/容器与跨迭代 ADR。
业务侧（product / glossary / core-domain-model / iterations）是 `ba-arch-plan` 的产出，本 skill 只读。

## 前置

- harness 已铺好（`{{AGENTS_FILE}}`、`{{DOCS_DIR}}/`）
- 已读 `{{STANDARDS_DIR}}/architecture.md`、`{{STANDARDS_DIR}}/adr.md`
- **业务边界已定**：`{{ARCHITECTURE_DIR}}/business/` 至少有 product 一句话与核心聚合；
  没有就先用 `ba-arch-plan`（先画图再定边界，图必重画）

## 输出位置

| 路径 | 内容 |
|---|---|
| `{{ARCHITECTURE_DIR}}/README.md` | 索引与分工（与 `ba-arch-plan` 共同维护） |
| `{{ARCHITECTURE_DIR}}/tech/c4-context.md` | C4 系统上下文 / 集成（PlantUML） |
| `{{ARCHITECTURE_DIR}}/tech/c4-container.md` | C4 容器（PlantUML） |
| `{{ADR_FILE}}` | 跨迭代 ADR（一张表，每条一句话） |

**不输出** `business/` 正文 —— 那是 `ba-arch-plan` 的落点；本文只读它来做切分依据。

## 硬性约束

- **意图 ≠ as-built**：ADR 与 C4 写目标取舍；实现细节专题仍在 `{{TECH_TOPIC_DIR}}/`
- **容器必须能承载核心聚合**；切分依据是 `{{ARCH_DOMAIN_MODEL_DOC}}` 的核心聚合 + 关键字段，不是代码目录
- 核心领域模型（仅核心聚合+关键字段）在 `{{ARCH_DOMAIN_MODEL_DOC}}`；全量 as-built 在 `{{DOMAIN_MODEL_DOC}}`
- 术语表唯一权威：`{{GLOSSARY_FILE}}`
- 迭代级细节写 `{{FEATURES_DIR}}/<迭代>/high-level-design.md`，不要塞进 C4
- 新 ADR：在 `{{ADR_FILE}}` 表追加一行一句话；按 `{{STANDARDS_DIR}}/adr.md`
- 路径不要写死成某台机器的绝对路径

## 与其它 skill

| Skill | 关系 |
|---|---|
| `ba-arch-plan` | 前置：业务边界、术语、核心聚合由它起草；本 skill 读它做切分 |
| `tl-high-level-design` | 继承本目录 ADR/C4；写本迭 HLD |
| `tl-arch-sync-back` | 实现漂移后对齐技术侧 |
| `ba-arch-sync-back` | 业务侧术语/领域/产品对齐 |
| `ba-write-spec` | 术语写入 `{{GLOSSARY_FILE}}` |

## 自检

- [ ] C4 两图可读，外部系统与容器职责清楚
- [ ] 每个容器能说清承载哪些核心聚合（能对上 `{{ARCH_DOMAIN_MODEL_DOC}}`）
- [ ] 已接受 ADR 有索引；与 `{{STANDARDS_DIR}}` 无冲突
- [ ] 没有往 `business/` 里写正文（那是 `ba-arch-plan` 的活）
- [ ] `{{ARCHITECTURE_DIR}}/README.md` 的技术侧链接可点、业务侧条目存在
- [ ] 已提示：进迭代前 architecture 须可读
