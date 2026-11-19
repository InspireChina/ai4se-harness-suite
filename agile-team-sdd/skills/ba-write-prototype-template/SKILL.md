---
name: ba-write-prototype-template
description: 按已写好的需求规格做一版可点击原型，放到该迭代的 prototypes 目录。规格写完、需求质量门之前使用。只做一次。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# 编写原型

对照 `{{FEATURES_DIR}}/<迭代>/<CODE>-<slug>/spec.md` 的字段和页面，做一版原型。

## 输出

- 原型放在 `{{FEATURES_DIR}}/<迭代>/prototypes/`
- 在原型目录的 README 里写清怎么启动、端口、对应哪份 spec

## 硬性约束

- 没有 spec 就停止
- 不改后端实现
- 同一份 spec 已经有原型时，只补缺的页面，不另起一套
