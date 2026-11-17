# Plan：dev-build 进度文件（粗 plan → 细 progress）

> 日期：2026-11-17  
> 状态：已完成

## 目标

- `dev-plan` 在 plan 中只写 **粗粒度「实施步骤」**（约 5～10 条）
- `dev-build` 在同目录写 `{planStem}-progress.md`，把粗步骤 **细化** 为 checklist 并实时勾选

## 命名

| plan | progress |
|---|---|
| `plan.md` | `plan-progress.md` |
| `plan-{slug}.md` | `plan-{slug}-progress.md` |

## 验证

- `PATH_MODE=relative ./agile-team-sdd/install.sh example-project --force`
- `./.agents/verify.sh`
