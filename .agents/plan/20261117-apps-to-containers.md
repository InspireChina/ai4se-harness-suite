# apps → containers 目录重命名

> 日期：2026-11-17
>
> **plan 一旦定稿就不修改。**
>
> 状态：**已确认执行**（2026-11-17）

## 1. 目标

将 `example-project/apps/` 整体迁到 `containers/`，并同步 harness 占位符默认值与安装器探测，使新装项目默认为 `containers/backend|frontend`。

## 2. 映射

| 旧 | 新 |
|---|---|
| `containers/backend` | `containers/backend` |
| `containers/frontend` | `containers/frontend` |
| `containers/` | `containers/` |

## 3. 验证

`PATH_MODE=relative ./agile-team-sdd/install.sh example-project --force` + `./.agents/verify.sh`
