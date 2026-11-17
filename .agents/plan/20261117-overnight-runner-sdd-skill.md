# Plan：overnight-runner 并入 agile-team-sdd（无前缀）

> 日期：2026-11-17  
> 状态：已完成

## 约定

- 模板：`agile-team-sdd/skills/overnight-runner-template/`（frontmatter `overnight-runner-template`）
- 安装后：`.agents/skills/overnight-runner/`（**无** ba/dev/qa 前缀）
- catalog 分组：`runner`
- 删除 `overnight-runner/SKILL.md`，避免与 example 已安装副本重名；人读文档仍用 `overnight-runner/README.md`
- `opencode.jsonc` 去掉对 `overnight-runner` 目录的 skills 路径（改由 SDD 安装）
- 全库「17 个 skill」→「18 个」

## 验证

`PATH_MODE=relative ./agile-team-sdd/install.sh example-project --force`  
`./.agents/verify.sh`
