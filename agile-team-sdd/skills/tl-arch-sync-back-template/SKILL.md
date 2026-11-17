---
name: tl-arch-sync-back-template
description: 技术侧回写对齐：architecture ADR/C4 与实现、facts 非 ADR 专题之间的漂移。当实现推翻或细化了跨迭代技术取舍时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# TL：架构技术侧 sync-back

规格/实现演进后，对齐 **技术意图**（`{{ARCHITECTURE_DIR}}/tech/`）与 **as-built**（代码 + `{{TECH_TOPIC_DIR}}/`）。

## 前置

- 已知漂移点（新依赖、换鉴权、分层变化、HLD 开放决策落地等）
- 已读 `{{ADR_FILE}}` 与 `{{TECH_TOPIC_DIR}}/` 专题

## 做什么

1. 对照代码与 `{{TECH_TOPIC_DIR}}/`，列出与 ADR/C4 不一致项
2. 若取舍仍成立：更新实现专题或代码注释，**不改**已接受 ADR 一句话语义
3. 若取舍被推翻：在 `{{ADR_FILE}}` 将旧条标已废弃，并新增一行一句话决策；更新 C4 若边界变了
4. 更新 `{{ARCHITECTURE_DIR}}/README.md` 若需要
5. 迭代 HLD 若仍引用旧编号，改表或说明（历史 plan 定稿可不改语义）

## 不要做

- 不要把单 feature 细节写进 ADR
- 不要删 as-built 专题冒充「只留意图」
- 不要改 `{{DOMAIN_MODEL_DOC}}` / glossary（那是 `ba-arch-sync-back`）

## 自检

- [ ] 每个漂移项有结论：修实现 / 补专题 / 新 ADR
- [ ] ADR 索引与状态一致
- [ ] C4 与当前部署边界一致（或标明「意图未落地」）
