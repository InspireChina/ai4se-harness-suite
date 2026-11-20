# 团队 AI 编程工作流指南

本目录以 **HTML 单页** 为主文档（便于预览矩阵图与排版）：

- **→ 打开 [`index.html`](index.html)**：总览矩阵 + 三个阶段 + 测试分层 + 角色手册；顶部用 `<iframe>` **嵌入泳道图**
- **→ 打开 [`flow.html`](flow.html)**：角色 × 阶段泳道图本身（可缩放 / 拖拽；被嵌入的就是它）

在线看（GitHub Pages 从 `main` 构建，推送后生效）：

- <https://inspirechina.github.io/ai4se-harness-suite/team-workflow-guide/>
- <https://inspirechina.github.io/ai4se-harness-suite/team-workflow-guide/flow.html>

两张图分工：`index.html` 讲 **每个阶段做什么、吃什么输入、吐什么产物**；
`flow.html` 讲 **谁在哪一列、怎么交接、在哪儿被打回** —— 3 条打回边、3 道人工闸门，
外加两处细节：`dev-build` 一个节点里列出的四步 LOOP（实现 → 自测 → UI 对照 → 代码评审，不绿就继续改）、
`overnight-runner` 的队列（卡片堆 = 可一直追加，只收已确认 plan）。

## 这是 L3 模式

本指南描述 **AI4SE L3** 的协作方式 —— **Human in the loop**，**人是编排者**：
由人决定下一步做什么、交给哪个角色、什么时候推进；AI 一次只执行被点名的那一步。

| 维度 | 本指南（L3） | [`agents-workflow-engine`](../agents-workflow-engine/)（L4） |
|---|---|---|
| 成熟度 | AI4SE **L3** | AI4SE **L4** |
| 人机关系 | **Human in the loop**，人在环内 | **Human on the loop**，人看着环 |
| 人的角色 | **编排者**：排期、分工、按节奏推进 | **决策者**：只在闸门与异常处拍板 |
| 谁在调度 | 人按阶段点名 skill | 图按节点自动调度子 agent |
| 上下文 | 会话 + 仓库文档，靠人带下去 | 图实例目录（状态 / 决策 / 产物），不依赖会话 |
| 适合 | **敏捷团队**：多角色、节奏由人定 | **FDE 工作者**：一人扛完整条线 |
| 看哪张图 | [`flow.html`](flow.html)（角色泳道） | [`graph.html`](../agents-workflow-engine/graph.html)（节点与闸门） |

两者共用同一套 27 个 SDD skill，差别只在 **谁调度**：人拉（L3）还是图跑（L4）。

内容覆盖：

0. 总览矩阵（人 / AI 动作 / skill / 输入 / 输出）
1. 项目准备（TL 装机定规）
2. 迭代前：BA 规格+原型 · TL 高阶 TRD · QA 用例（并行）
3. 迭代中：DEV 写 Plan → 实现 · QA 验收 · TL 发布 / PM 复盘
4. 测试分层与归属
5. 角色手册（BA / PM / TL / DEV / QA / AI）
6. Skill 对照

规范硬约束仍在各项目的 `AGENTS.md`。本指南讲 **人怎么配合**。