# 技术设计：ADR 约定 + 迭代高阶设计 + tl-high-level-design

> 日期：2026-11-17
>
> **plan 一旦定稿就不修改。**
>
> 状态：**已确认执行**（2026-11-17）

## 1. 目标

1. `docs/standards/` 增加 ADR 写法约定与模板；已有 ADR 仍留 `docs/facts/tech-topic/`。
2. 每个迭代目录落 `high-level-design.md`（iteration1 提供骨架）。
3. 新增 skill `tl-high-level-design`（catalog `tl` 组），并回写 harness。

## 2. 约定

- HLD 路径：`docs/features/<迭代>/high-level-design.md`；确认前不得写 feature Plan。
- ADR 写法：`docs/standards/adr.md` + `templates/adr.md`；正文落盘 `docs/facts/tech-topic/NNN-slug.md`。

## 3. 验证

`PATH_MODE=relative ./agile-team-sdd/install.sh example-project --force` + `./.agents/verify.sh`
