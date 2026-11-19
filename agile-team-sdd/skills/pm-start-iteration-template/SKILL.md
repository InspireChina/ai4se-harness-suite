---
name: pm-start-iteration-template
description: 根据人给出的版本名启动一次迭代，建立 docs/features 下的迭代目录。当 graph 主会话进入「开始版本」之后、编写规格之前使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# 启动迭代

主会话已经问过人「开始版本」。本 skill 只负责把这次迭代的目录落下来。

## 输入

- 版本名，例如 `iteration1`
- 一句话范围

## 做法

1. 在 `{{FEATURES_DIR}}/<版本名>/` 建立目录（已存在则不覆盖里面的规格）
2. 写 `{{FEATURES_DIR}}/<版本名>/iteration.md`：版本名、范围、日期
3. 不要写 spec，不要写 plan

## 硬性约束

- 版本名只含字母、数字、连字符
- 不创建 feature 子目录；那是 `ba-write-spec` 的事
