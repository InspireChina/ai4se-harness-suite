# 把两张图收进模块 + iframe 嵌入 + GitHub Pages 链接

## 目标

1. `team-workflow-guide/index.html` 用 `<iframe>` 嵌入 `flow.html`，读者不必跳页。
2. 编排图从 `.agents/plan/iteration-to-test.html` 移到 `agents-workflow-engine/graph.html`（图是模块产物，不该留在计划目录）。
3. 两个模块 README 都给出 GitHub Pages 链接。

## 改动

| 位置 | 改动 |
|---|---|
| `.agents/plan/iteration-to-test.html` → `agents-workflow-engine/graph.html` | `git mv`（保留历史）；顺手把过时的标题「版本到提测」改成「迭代编排图」（图早已跑到「可上线」），并加副标题「从需求到可上线 · 主会话按图调度子 agent（L4 · 人只在岔路口决策）」 |
| `team-workflow-guide/index.html` | 新增首屏 `#lane` 段：`.figure` 卡片 + `.figure-bar`（工具条 / 新窗口打开）+ `<iframe src="flow.html" title=... loading="lazy">` + `.figure-hint` 降级链接；导航「角色协作图」改为锚点 `#lane`，lead 指向 `#lane` |
| `team-workflow-guide/flow.html` | 「← 返回指南」加 `target="_top"`（在 iframe 里也能跳出框架）；legend hint 补「双击适应窗口」 |
| `agents-workflow-engine/README.md` | 新增「## 图」段：Pages 链接 + 本地 `graph.html` + 「`render` 只出 Mermaid，HTML 是手工人读版」；维护段同步 |
| `team-workflow-guide/README.md` | 说明 index.html 嵌了 flow.html；补两条 Pages 链接；L3/L4 对照表的「看哪张图」指向 `../agents-workflow-engine/graph.html` |
| 根 `README.md` | 「看哪张图」行改为 `flow.html` / `graph.html` + 两条 Pages 链接（原链指向已移动的 `.agents/plan/...`） |
| `AGENTS.md` | §8 模块表补「含人读图 `graph.html`」；§13 目录树加 `graph.html`、注明 index.html 首屏 iframe；§13 同步要求加「改预设 → 同步 `graph.html`」 |

## 取舍

| 决定 | 原因 |
|---|---|
| iframe 高 560px（窄屏 420px），`loading="lazy"` | 图的纵向比例在适应窗口后约 1:4，560px 留够缩放余量且不把下面正文挤出首屏 |
| 不在 README 里放 `<iframe>` | GitHub 会剥掉 HTML 标签；Pages 才是交互入口，README 给链接 |
| 不引用 `.images/l4-graph.png` | 那张截图停在「人工补测」，与现在的图（到「可上线」）不一致，引用会误导 |
| 不加 `.nojekyll` | Pages 正用 Jekyll 把根 `README.md` 渲成首页；加 `.nojekyll` 会让根路径 404 |

## 验证

- `./.agents/verify.sh` 全绿（含 160+ 条 Markdown 相对链接，检查 `graph.html` 新路径没断链）
- 浏览器实测 `index.html`：iframe 加载出 18 个实心节点、0 console 报错、无横向溢出
- `graph.html` 直接打开正常出图，标题为新文案

## 不做

- 不改两张图的视觉设计（本轮只搬位置、加嵌入与链接）
- 不推送、不提交（Pages 从 `main` 构建，推上去才生效）
