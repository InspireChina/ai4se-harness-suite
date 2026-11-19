# 团队协作泳道图 + L3 / L4 双模式说明

> 状态：**已完成**（2026-11-19）。
> 验证：`node --check` 通过；浏览器实测 17 节点 / 20 连线 / 0 节点重叠 / 0 console 报错；
> `./.agents/verify.sh` 68 项全绿（含 160 条相对链接）。

## 背景

`agents-workflow-engine` 已经有一张泳道图（`.agents/plan/iteration-to-test.html`）：
**列 = 时间，行 = 人在环上的位置（human / master / sub）**，回答「图**怎么**调度」。

`team-workflow-guide` 只有 HTML 矩阵（阶段 × 角色 × skill × 输入输出），缺一张能一眼看清
「五个人怎么交接、在哪儿被打回」的图。所以在 guide 目录新增 `flow.html`：
**行 = 角色（BA / PM / TL / DEV / QA），列 = 时间**，与引擎那张互补而不重复。

同时把两种成熟度写进 README，避免选型时把两张图、两个模块看混：

- `team-workflow-guide`：AI4SE **L3**，Human in the loop，**人是编排者**，适合敏捷团队
- `agents-workflow-engine`：AI4SE **L4**，Human on the loop，**人是决策者**，适合 FTE 工作者

## 改动

| 文件 | 改动 |
|---|---|
| `team-workflow-guide/flow.html` | 新增：5 泳道 × 16 列，17 节点、20 连线（17 正向 + 3 打回），4 段阶段带，3 条分隔线 |
| `team-workflow-guide/index.html` | 目录加「角色协作图」入口；lead 加链接；§0 增一句 L3 / L4 定位 |
| `team-workflow-guide/README.md` | 两张图分工 + **L3 / L4 对照表** |
| `README.md` | 新增「两种协作模式：L3 与 L4」小节；模块表两行加 L3 / L4 标记 |
| `AGENTS.md` | §3 / §8 措辞（纯文档可含渲染型页面脚本）；§13 目录树补 `flow.html` 与 `agents-workflow-engine`；同步要求补 `flow.html` |
| `.agents/plan/iteration-to-test.html` | 修 `Gate` 内框 `calc(w - 8)` 不生效（内框 0×0），闸门恢复双层边框 |

## 图上内容的事实来源

节点、角色归属、闸门位置全部对齐 `index.html` 的总览矩阵与 `AGENTS.md` §8 的数据流，**没有新增流程**：

- 项目准备：`/harness-installer` → `/tl-arch-plan` → 定方向 · 首迭范围
- 迭代前：规格 + 原型 → 估算 →（TRD★确认 ∥ 文本用例 TC）→ DoR 齐备
- 迭代中：写 Plan★确认 → Plan 质量门 → 实现·自测·UI·评审 → E2E + 手工 + 冒烟 → QA 验收★
- 交付与复盘：事实同步·MR → 上线清单 → 复盘·回写 → 可上线
- 3 条打回边：TRD → 规格、Plan 质量门 → 写 Plan、QA 验收 → 实现

## 技术取舍

| 取舍 | 原因 |
|---|---|
| 复用 `iteration-to-test.html` 的骨架，只换数据层 | 缩放 / 平移 / 图例 / 形状全复用，视觉同款；改的是 lane、cells、columns、links、stages |
| 列 = 时间、行 = 角色 | 与引擎图（行 = 人在环位置）互补，两张图不会看混 |
| TC 与 TRD 同列并行，TC 从估算底部绕入 | 并行关系要贴在一起；绕行避免连线穿过 TRD 方框（原按左通道会穿框且箭头倒指） |
| 打回边红色虚线，标签放在线**旁边** | 标签压线会吃掉虚线段，旁置后 3 条线全可见 |
| 保留 JointJS CDN | 与既有页面一致；断网时页面显示「没有加载」提示，不白屏 |

## 第二轮（同日）：加 overnight-runner 队列

| 改动 | 说明 |
|---|---|
| 新增 `overnight-runner` 节点（Plan 质量门之后、dev-build 之前） | 队列用「卡片堆」表示可一直追加（两层虚线卡片右缘对齐、只在顶部露头）；副标题「队列 · 可一直追加」 |
| 队列标注 | 「＋ 随时追加 · 只收已确认 plan」，放在卡片堆上方的空档里，不压线不压框 |
| DEV 泳道 150 → 240，QA 泳道下移 | 给队列与标注留纵向空间；图变高不影响适应窗口比例（宽度主导） |
| 阶段带 | 第 3 段扩到 `boundaryX(13)`（含 QA 验收★），第 4 段为事实同步 / 上线清单 / 复盘 / 可上线 |
| 图例 | 加「队列 · 可追加」「细节节点」两项 |

「只收已确认 plan」取自 `index.html` §3 的 callout。

## 第三轮（同日）：dev-build 改回单节点 + 框内步骤清单

第一版把 `dev-build` 拆成虚线容器 + 四个子节点 + 三条内部箭头，图上凭空多出 5 个节点，
读者要在两层框里找线。改成 **一个节点**：照 `iteration-to-test.html` 里 `workflow.Build` 的样式
（标题 / 副标题 / 左对齐编号清单 / 脚注），步骤直接写在框里。

| 改动 | 说明 |
|---|---|
| 删掉虚线容器、四个子节点、三条内部箭头 | 主链回到一列一个节点，`队列 → dev-build → E2E` 一条线走完 |
| `workflow.Build`（184 × 176） | 标题 `/dev-build`；副标题「全栈 LOOP · 以记录为准」；清单 1 实现（前后端）／2 自测 · self-test.md／3 UI 对照 · ui-review.md／4 代码评审；脚注「不绿就继续改，直到记录全绿」 |
| DEV 泳道 300 → 240 | 节点自带宽高，泳道只留上下各 32px |
| 图例「展开的子步骤」→「细节节点」 | 对应 2px 粗边实心框 |

事实来源：清单取自 `agile-team-sdd/skills/dev-build-template/SKILL.md` 的 LOOP checklist
（实现 → `dev-self-test` → `dev-ui-review` → `dev-code-review`，以 `*-self-test.md` / `*-ui-review.md` 通过为准）。

验证：`node --check` 通过；浏览器几何实测 18 个实心节点 / 21 条连线 / 0 节点重叠 / 0 文字溢出 /
0 连线穿实心框 / 0 console 报错；队列与 dev-build 中心线误差 0 px，`队列 → dev-build` 为单段水平线；
框内 4 行清单 + 脚注全部落在框内（最长 139.5 px < 164 px 可用宽，最低一行距底边 17.3 px）；
打回虚线终止于 dev-build 底边中点 (2438, 664)、箭头朝上；适宽约 17%。

## 不做

- 不在 `flow.html` 里画 L4 的节点调度（那是 `iteration-to-test.html` 的事）
- 不改 `index.html` 的矩阵内容（本轮只加入口与定位说明）
- 不把 `flow.html` 装进目标项目（guide 是仓库文档，不是 skill 产物）