---
name: tl-arch-plan-template
description: 编写或更新项目级高阶架构 docs/architecture/（C4、ADR、与业务侧对齐）。当项目准备阶段定技术边界、或跨迭代架构需落盘时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# TL：项目级架构设计（Architecture Plan）

在 **项目准备** 或跨迭代演进时，维护 `{{ARCHITECTURE_DIR}}/` 高阶意图（技术侧为主，业务侧与 BA 协作）。

## 前置

- harness 已铺好（`{{AGENTS_FILE}}`、`{{DOCS_DIR}}/`）
- 已读 `{{STANDARDS_DIR}}/architecture.md`、`{{STANDARDS_DIR}}/adr.md`
- 业务侧至少有产品边界草稿（可与 BA 同轮用本 skill 补齐 `business/`）

## 输出位置

| 路径 | 内容 |
|---|---|
| `{{ARCHITECTURE_DIR}}/README.md` | 索引与分工 |
| `{{ARCHITECTURE_DIR}}/tech/c4-context.md` | C4 系统上下文 / 集成（PlantUML） |
| `{{ARCHITECTURE_DIR}}/tech/c4-container.md` | C4 容器（PlantUML） |
| `{{ADR_FILE}}` | 跨迭代 ADR（一张表，每条一句话） |
| `{{ARCHITECTURE_DIR}}/business/` | 与 BA：glossary / product / core-domain-model（核心+关键字段）/ iterations |

## 硬性约束

- **意图 ≠ as-built**：ADR 与 C4 写目标取舍；实现细节专题仍在 `{{TECH_TOPIC_DIR}}/`
- 核心领域模型（仅核心聚合+关键字段）写 `{{ARCH_DOMAIN_MODEL_DOC}}`；全量 as-built 写 `{{DOMAIN_MODEL_DOC}}`
- 术语表唯一权威：`{{GLOSSARY_FILE}}`
- 迭代级细节写 `{{FEATURES_DIR}}/<迭代>/high-level-design.md`，不要塞进 C4
- 新 ADR：在 `{{ADR_FILE}}` 表追加一行一句话；按 `{{STANDARDS_DIR}}/adr.md`
- 路径不要写死成某台机器的绝对路径

## 与其它 skill

| Skill | 关系 |
|---|---|
| `tl-high-level-design` | 继承本目录 ADR/C4；写本迭 HLD |
| `tl-arch-sync-back` | 实现漂移后对齐技术侧 |
| `ba-arch-sync-back` | 业务侧术语/领域/产品对齐 |
| `ba-write-spec` | 术语写入 `{{GLOSSARY_FILE}}` |

## 自检

- [ ] C4 两图可读，外部系统与容器职责清楚
- [ ] 已接受 ADR 有索引；与 `{{STANDARDS_DIR}}` 无冲突
- [ ] business 侧有 glossary 或 product 边界；iterations 指向真实迭代目录
- [ ] 已提示：进迭代前 architecture 须可读
