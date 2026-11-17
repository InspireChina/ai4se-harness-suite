# Plan：dev-build 编排依赖 skill（全栈闭环）

> 日期：2026-11-17  
> 状态：已完成

## 约定

`dev-build` 定位为 **全栈实现编排器**（非只写代码）：

```
实现（前后端）→ dev-self-test →（有 UI）dev-ui-review → dev-code-review
       ↑________________ 失败 / 评审问题：修 bug 后回到对应步骤 ________↓
```

- 修 bug：优先按 `dev-self-test` / `dev-debug`（chrome-mcp）排查，再回到自测
- 子 skill 正文不合并进 build；build **调用并按顺序执行**它们的流程
- 同步 `team-workflow-guide/index.html` 与套件表格 / catalog

## 验证

`PATH_MODE=relative ./agile-team-sdd/install.sh example-project --force`  
`./.agents/verify.sh`
