---
name: ba-requirement-review-template
description: 用与写规格不同的模型审查 spec，只回答满意或不满意。需求规格和原型写完之后、人做需求决策之前使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# 需求质量门

读 `{{FEATURES_DIR}}/<迭代>/<CODE>-<slug>/spec.md`。这是对抗验证，不要沿用写规格时的模型。

## 检查

- 验收标准能不能单独拿去测
- 字段、角色、错误情况是否写全
- 术语是否指向 `{{GLOSSARY_FILE}}`

## 输出

最后一行只能是 `满意` 或 `不满意`。

不满意时，在前面用短句列出要改的点。不要改 spec 本身。
