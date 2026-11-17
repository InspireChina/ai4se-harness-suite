---
name: ba-arch-sync-back-template
description: 业务侧回写对齐：术语表、领域模型意图、产品概念与 features / facts as-built。当规格或实现导致统一语言或领域结构漂移时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# BA：架构业务侧 sync-back

对齐 **业务意图**（`{{ARCHITECTURE_DIR}}/business/`）与 **过程/事实**（`{{FEATURES_DIR}}/`、`{{DOMAIN_MODEL_DOC}}`）。

## 双份领域模型

| 文件 | 性质 |
|---|---|
| `{{ARCH_DOMAIN_MODEL_DOC}}` | Core 意图：核心聚合 + 关键字段 |
| `{{DOMAIN_MODEL_DOC}}` | as-built：与代码一致的全量模型 |

本 skill 负责两边对齐；`ba-gen-facts` 主要校准 as-built。Core 文档**不要**堆全量字段。

## 前置

- 术语权威：`{{GLOSSARY_FILE}}`
- 相关 feature `spec.md` / 已实现聚合类可查

## 做什么

1. 扫本轮新术语 / 改名：更新 `{{GLOSSARY_FILE}}`；检查 spec 引用仍指向该文件
2. 对照代码与 `{{DOMAIN_MODEL_DOC}}`：补 as-built
3. 对照产品边界：更新 `{{ARCHITECTURE_DIR}}/business/product.md`、`iterations.md` 若里程碑变了
4. 若核心聚合/关键字段需演进：更新 `{{ARCH_DOMAIN_MODEL_DOC}}`（仍只写核心+关键字段）；未实现的核心概念可标注
5. 与 TL 确认是否需联动 `tl-arch-sync-back`（技术边界变了才转交）

## 不要做

- 不要在 `{{FEATURES_DIR}}/` 下再建第二份 glossary
- 不要用 as-built 静默覆盖意图而不标注「未实现」
- 不要改 ADR / C4（`tl-arch-sync-back`）

## 自检

- [ ] glossary 无重复中文键；spec 引用路径正确
- [ ] 意图与 as-built 差异有说明或已消除
- [ ] product / iterations 与当前迭代 README 不矛盾
