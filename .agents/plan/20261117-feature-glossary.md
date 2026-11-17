# Feature 术语表（双语统一语言）

> 日期：2026-11-17
>
> **plan 一旦定稿就不修改。**
>
> 状态：**已确认执行**（2026-11-17）

## 1. 目标

每个 feature 目录增加 `glossary.md`（中英双语），服务统一语言；模板 + `ba-write-spec` 约定同步；iteration1 九份填实。

## 2. 约定

| 中文 | 英文 | 说明（可选） |
|---|---|---|
| 备注 | remark | |

`spec.md` 引用：§2 附近「术语表见」+ 指向同目录 `glossary.md` 的相对链接。

## 3. 验证

`PATH_MODE=relative ./agile-team-sdd/install.sh example-project --force` + `./.agents/verify.sh`
