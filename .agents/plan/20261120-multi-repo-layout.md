# 指南加一章：多仓库布局（单仓 / 嵌套 / 并列）

## 目标

`team-workflow-guide/index.html` 新增 **§7 仓库布局**：把「harness 与业务代码怎么放」讲清楚，
给出三种形态的适用条件、目录长相、落地命令与各自的坑，并明确推荐「嵌套仓库」。

读者是 **TL**（§1 装机时就要定布局），所以放在 §6 之后作为收尾章节，不改动既有编号与锚点。

## 不做什么

- 不动 `flow.html`（布局不属于某个阶段节点，泳道图没有它的位置）
- 不动任何 skill / 安装器 / 占位符（`containers/` 与 `PATH_MODE` 已经支持这三种形态）
- 不给 `example-project` 真挂 submodule：它是单仓形态的参考实现，`containers/` 保持「扩展位」
  （与 `.agents/plan/20261117-example-project-layout-and-facts.md` 的结论一致）
- 不改 `example-project/AGENTS.md`（它描述的是单仓样例的目录，不承担通用布局说明）

## 改动清单

| 文件 | 改什么 |
|---|---|
| `team-workflow-guide/index.html` | TOC 加 `7. 仓库布局`；新增 `<section id="repos">`；§1.2 第 1 步加一句「先定布局」；§1.3 出口条件加一条 |
| `team-workflow-guide/README.md` | 「内容覆盖」列表补第 7 条 |
| `README.md`（根） | 实践表里的 `Mono repo` 行改成 `仓库布局`，说明三种形态并链到 `index.html#repos` |

## §7 正文结构

### 7.0 一句话 + 决策表

> 默认选 **嵌套**：主仓库装 harness，业务组件以 submodule 挂在 `containers/<组件>`。
> 只有当「组件少、没人管权限」或「harness 要给多个产品复用」时才偏离。

| 你的情况 | 选 | 一句话理由 |
|---|---|---|
| 一个产品、前后端 + 文档都是同一拨人 | 方式一 单仓 | 路径最简单，没有指针要维护 |
| 业务代码已有独立仓库 / 要按组件切权限与发布 | **方式二 嵌套（推荐）** | 目录路径与单仓完全一致，skill 与占位符零改动 |
| harness 是平台团队交付物，要服务 N 个产品 | 方式三 并列 | 解耦彻底，代价是 CI 与文档链接都要跨仓 |

### 7.1 三种形态对比

| 维度 | 一 · 单仓 | 二 · 嵌套（推荐） | 三 · 并列 |
|---|---|---|---|
| 目录长相 | 一个仓全装下 | 主仓 + `containers/*` 子模块 | 两个平级仓库，靠 `../` 关联 |
| harness 在哪 | 同仓 | 主仓（与 docs 同级） | 独立仓 |
| clone 后能用 | 直接 | 要 `--recurse-submodules` | 要 clone 两个仓且保持目录结构 |
| 权限边界 | 无（全员全仓） | 按组件仓切，主仓只放文档与 harness | 按仓切，harness 可只读 |
| agent 工作区 | 一个目录 | **一个目录**（子模块就在里面） | 两个目录，agent 通常只能看一个 |
| 升级 harness | 直接改 | 主仓单独一次提交 | 独立仓发版，各产品各自跟进 |
| 主要代价 | 仓库膨胀、CI 全量 | 指针要跟着子仓提交走 | 跨仓路径与链接极易断 |

### 7.2 方式一 · 单仓（mono repo）

```text
my-product/
├── AGENTS.md  .agents/skills/  .mcp.json
├── docs/            architecture · features · facts · standards
├── containers/      backend/  frontend/      ← 就是普通目录
└── e2e/
```

- 适合：单产品、组件 1–3 个、团队规模小；**新项目起步的默认选择**
- `example-project/` 就是这个形态 —— 先按它长起来，撑不住再迁
- 坑：仓库变大后 clone 慢、CI 每次全量、没法「后端仓只给后端同学写权限」
- 迁移前先看：一个目录超过 ~2GB 或 CI 全量超过 15 分钟，就该考虑拆

### 7.3 方式二 · 嵌套仓库（推荐）

```text
my-product/                    ← 主仓库：harness + 文档 + 胶水
├── AGENTS.md
├── .agents/skills/            ← 27 个 skill（随主仓分发）
├── docs/                      ← architecture / features / facts / standards
├── containers/
│   ├── backend/               ← submodule → git@…/svc-backend.git
│   └── frontend/              ← submodule → git@…/web-app.git
└── e2e/
```

**为什么推荐**：`containers/backend` 与单仓里的普通目录**路径完全一样**，
所以 `AGENTS.md`、27 个 skill、占位符（`BACKEND_DIR` / `FRONTEND_DIR`）、测试命令
（`cd containers/backend && mvn test`）一个字都不用改；`init-harness.sh` 探测本来就优先
`containers/backend|frontend`。权限与发布仍按子仓库走，agent 只要打开主仓一个工作区。

命令：

```bash
# 主仓里挂子仓（子仓必须已有远端仓库）
git submodule add git@github.com:org/svc-backend.git containers/backend
git submodule add git@github.com:org/web-app.git  containers/frontend

# 新人 clone（漏了 --recursive 就补这一步）
git clone --recurse-submodules git@github.com:org/my-product.git
git submodule update --init --recursive
```

铁律：

1. **先子仓、后主仓**：代码改动必须先在 `containers/backend` 里 commit + push，
   再回主仓 commit 那个指针。反了就等于「主仓指向一个没有你代码的 commit」
2. **指针钉 commit，不钉分支**：要跟分支就显式 `git submodule update --remote`，
   并且知道 CI 会跟着漂
3. **文档只留主仓**：`docs/features/`、`docs/architecture/` 不进子仓库 —— 否则同一份规格两处版本
4. **子仓内的构建产物各自 ignore**：`containers/*/target`、`node_modules`、`dist` 在各自仓里管
5. **子仓可见性**：看不到子仓的人等于看不到代码；至少要读权限，CI 用机器账号拉

### 7.4 方式三 · 独立 harness 仓库（并列）

```text
workspace/
├── harness/     ← 上下文 + skills + 文档骨架（独立仓库，平台团队维护）
└── product/     ← 业务代码（独立仓库）
```

- 关联靠**相对位置**：`../harness`、`../product`
- 装进 `product` 的产物必须用 `PATH_MODE=relative`（绝对路径会把别人的 home 目录写进 skill）
- **最大的坑是 agent 的工作区边界**：IDE Agent 通常只认打开的那个目录，
  `../harness/docs/...` 多半读不到。现实里只有两种用法：
  - **人切换目录**：装 harness 时人站在 `product`，需要查架构文档时再切到 `harness`
  - **agent 双开**：agent 在 `product` 里干活，把 `harness` 用符号链接或 submodule 挂进来 ——
    这时其实已经退化成方式二
- 适合：多个产品共用一套流程；harness 有独立发版节奏；harness 仓允许只读
- 坑：CI 要 checkout 两次（`actions/checkout` 的 `path:` 参数）、跨仓相对链接一改就断、
  MR 里看不到「流程改动 + 代码改动」的完整 diff

### 7.5 三种形态下的 harness 升级动作

| 形态 | 升级 harness 的命令 | 注意 |
|---|---|---|
| 单仓 | 直接在仓里跑三个安装器 | 与业务改动同一个 MR，容易一起评审 |
| 嵌套 | 在主仓跑三个安装器；**不要**在 `containers/*` 里跑 | 子仓里的 skill 副本是无效副本 |
| 并列 | 在 `harness` 仓改，再 `PATH_MODE=relative` 装进 `product` | 装完要提交 `product` 里的 `.agents/` 与 `docs/` |

### 7.6 反模式

- 把 harness **复制**进多个仓各自改 → 立刻漂移，27 个 skill 各有各的版本
- 跨仓用**绝对路径**（`/Users/…`、`/home/…`）引用 harness → 换机器即断
- submodule 指向**个人分支** → 别人拉不到
- 子仓 A 里再挂子仓 B，深度超过两层 → 指针地狱，没人敢升级

## 与其它章节的交叉改动

| 位置 | 改什么 |
|---|---|
| §1.2 第 1 步 | 末尾加一句「多仓库项目先定布局（见 §7），布局决定 `AGENTS.md` 与文档写哪些路径」 |
| §1.3 出口条件 | 加一条「仓库布局已定：组件在 `containers/` 下就位（单仓 / 嵌套 / 并列都有明确说法）」 |
| TOC | `6. Skill 对照` 之后加 `7. 仓库布局` |

## 验证

1. `./.agents/verify.sh` 全绿（第 9 节查相对链接；本章不引入新链接目标）
2. 浏览器打开 `index.html`：TOC 能跳到 §7，三张表不溢出（窄屏横向滚动正常）、
   两段目录树代码块不换行错位、`§7` 的锚点 `#repos` 可达
3. 全文口径与根 `README.md` 的「仓库布局」行一致（三种形态名称、推荐结论）
