---
name: ba-requirement-review
description: 用与写规格不同的模型审查 spec，只回答满意或不满意。需求规格和原型写完之后、人做需求决策之前使用。
---

# 需求质量门

读 `docs/features/<迭代>/<CODE>-<slug>/spec.md`。这是对抗验证，不要沿用写规格时的模型。

## 检查

- 验收标准能不能单独拿去测
- 字段、角色、错误情况是否写全
- 术语是否指向 `docs/architecture/business/glossary.md`

## 输出

最后一行只能是 `满意` 或 `不满意`。

不满意时，在前面用短句列出要改的点。不要改 spec 本身。
