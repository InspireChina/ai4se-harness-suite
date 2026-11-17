# team-harness-suite

> **团队级 AI 基础设施。**
> 把散落在个人电脑上的 AI 编程经验，收敛成一套 **可安装、可交接、可复制** 的团队工具链。

## 为什么做这个

一个团队用 AI 编程，真正的瓶颈不是模型，而是 **没人知道该怎么用**：

- 每个人的 prompt、skill、调试手法都不一样，能力不可复制
- 换个人接手，所有上下文归零
- 工具（MCP、脚本、环境）全在个人机器上，别人跑不起来
- 流程靠口头约定，跳步、少测、文档不同步的问题反复出现

这个仓库把这些东西 **固化成资产**：

| 原来 | 现在 |
|---|---|
| 个人 skill | `agile-team-sdd/` 里的模板 + 一键安装 |
| 一份口头流程 | `team-workflow-guide/` 里的角色手册与流程定义 |
| 各人机器上的 MCP | `tool-chain-installer/` 统一安装到项目配置 |
| 每个人手搓的目录结构 | `harness-installer/` 一键铺好 `AGENTS.md` + `docs/` |
| 没有参照实现 | `example-project/` 一份完整可跑的例子 |

## 模块

| 模块 | 目录 | 目的 | 形态 |
|---|---|---|---|
| **SDD 技能套件** | [`agile-team-sdd/`](agile-team-sdd/) | 团队统一的开发流程 skill，17 个覆盖 BA→TL→PM→开发→QA→发布→复盘全流程。模板带占位符，可安装到任意项目 | skill + 安装脚本 |
| **Harness 初始化器** | [`harness-installer/`](harness-installer/) | 为任意项目铺好工程底座：`AGENTS.md`（架构与工程规范）+ `docs/` 文档骨架 + `opencode.jsonc` | skill + 模板 + 脚本 |
| **工具链安装器** | [`tool-chain-installer/`](tool-chain-installer/) | 把 MCP 工具链（chrome-devtools、playwright、context7…）写进项目配置，不依赖个人机器的全局状态 | skill + 工具清单 + 脚本 |
| **团队工作流指南** | [`团队工作流指南`](https://inspirechina.github.io/ai4se-harness-suite/team-workflow-guide/) | 团队级协作手册（HTML 单页）：总览矩阵 + 项目准备 → 迭代前设计 → 迭代中开发；角色、测试归属、闸门 | 文档 |
| **持续运行面板** | [`overnight-runner/`](overnight-runner/) | 把一串 plan 交给 coding agent 跑：左边任务队列、右边 agent 实时输出，看门狗自动重试，**多队列**各自独立，决策全程留痕（白天弹窗问你、夜里自动决策） | skill + Python 实现 |
| **参考实现** | [`example-project/`](example-project/) | 一份完整、可跑、已填满规范的全栈参考项目（Vue 3 + Spring Boot + DDD 四层），用来对照与教学 | 示例项目 |

## 关系图

```
                      team-workflow-guide/
                   （流程与角色约定 · 人看）
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
 harness-installer       agile-team-sdd       tool-chain-installer
  AGENTS.md 规范          17 个 SDD skill        MCP 工具链
  docs/ 文档骨架          BA·Dev·QA·PM 全流程
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                                ▼
                        example-project/
                     （参考实现 · 已装好全套）
```

## SDD 技能套件（17 个）

| 组 | Skill | 作用 |
|---|---|---|
| **BA** | `ba-grill-me` | 拷问需求，把模糊描述逼成可验收的规格 |
| | `ba-write-spec` | 编写需求规格：字段表、业务规则、权限矩阵、验收标准 |
| | `ba-gen-facts` | 从代码生成/校准事实文档：API、库表、领域模型、专题 |
| **TL** | `tl-high-level-design` | 写迭代高阶技术设计（HLD / TRD），确认前不得开 Plan |
| **Dev** | `dev-plan` | 实现前写技术方案，等待人工确认 |
| | `dev-build` | 按四层 DDD 约定实现，并维护细化进度文件 |
| | `dev-self-test` | 运行并修复开发自测 |
| | `dev-code-review` | 按项目规范做代码评审 |
| | `dev-ui-review` | 用 chrome-devtools-mcp 做界面评审 |
| | `dev-release-plan` | 整理迭代上线准备清单 |
| | `dev-create-mr` | 创建 Merge Request / Pull Request |
| **QA** | `qa-write-cases` | 编写 QA 用例（`TC-xxx` 文本 + 自动化） |
| | `qa-run-e2e` | 运行 E2E 用例集并定位失败 |
| | `qa-write-manual-plan` | 编写手动测试与冒烟用例计划 |
| **PM** | `pm-estimate` | 基于需求分类基线表估算工作量 |
| | `pm-retro` | 复盘并把改进项回写到 harness 本身 |

流程串起来：

```
ba-grill-me → ba-write-spec → pm-estimate
                    ↓
        ┌───────────┴───────────┐
 tl-high-level-design     qa-write-cases   ← 规格确认后并行
   （HLD 人工确认）
        └───────────┬───────────┘
                    ↓
              dev-plan（人工确认）→ dev-build → dev-self-test
                    ↓
      ba-gen-facts / dev-code-review / dev-ui-review
                    ↓
              dev-create-mr
                    ↓
      qa-run-e2e / qa-write-manual-plan   ← 合并闸门
                    ↓
            dev-release-plan → pm-retro → 改进 harness
```

## 实践索引

| 实践 | 说明 | 看哪里 |
|---|---|---|
| 团队级 SDD 框架 | 适合团队协作和拓展修改的 SDD 框架；纯 skill 驱动，与具体 agent 无关 | [`agile-team-sdd/`](agile-team-sdd/) |
| 夜间任务 | 把一串 plan 交给 coding agent 无人值守跑：多队列、看门狗重试、决策全程留痕（白天可弹窗、夜里自动兜底） | [`overnight-runner/`](overnight-runner/) |
| 团队流程手册 | 人怎么配合：总览矩阵、角色手册、测试归属与闸门；规范硬约束仍在各项目 `AGENTS.md` | [`team-workflow-guide/`](team-workflow-guide/index.html) |
| Agent as Code | 所有 Harness（skills、AGENTS、docs 骨架、MCP、overnight-runner）可安装进代码仓库，换机器 clone 即可用 | [`harness-installer/`](harness-installer/) · [`tool-chain-installer/`](tool-chain-installer/) |
| 高阶设计 | 迭代前写迭代级高阶方案（HLD / TRD），确认后再开 feature Plan，让迭代边界更稳定 | [`tl-high-level-design`](agile-team-sdd/skills/tl-high-level-design-template/SKILL.md) · [样例 HLD](example-project/docs/features/iteration1/high-level-design.md) |
| ADR | 跨迭代技术取舍写成架构决策记录；写法在 standards，正文落在 `docs/facts/tech-topic/` | [ADR 规范](example-project/docs/standards/adr.md) · [tech-topic 样例](example-project/docs/facts/tech-topic/001-4-layer-ddd.md) |
| 代码打样 | 迭代内用独立 Vite 原型先把交互与页面打通，规格与验收对齐后再进实现 | [iteration1 原型](example-project/docs/features/iteration1/prototypes/README.md) |
| 事实文档 | 实现后校准 `docs/facts/`，形成可靠知识库（API、库表、领域、专题） | [`ba-gen-facts`](agile-team-sdd/skills/ba-gen-facts-template/SKILL.md) · [facts](example-project/docs/facts/README.md) |

## 快速开始

### 体验现成的

```bash
cd example-project
cat AGENTS.md          # 一份填满的工程规范范本
ls .agents/skills/      # 已安装的 17 个 SDD skills
```

### 装到自己的新项目

```bash
# 1. 铺 harness：生成 AGENTS.md + docs/ 骨架
./harness-installer/scripts/init-harness.sh ../my-project

# 2. 装 SDD skills（渲染占位符 → 写进 .agents/skills/）
./agile-team-sdd/install.sh ../my-project

#    也可以只装某一组 / 某几个
./agile-team-sdd/install.sh ../my-project --group qa
./agile-team-sdd/install.sh ../my-project --skill dev-plan --skill pm-retro

# 3. 装 MCP 工具链
node tool-chain-installer/scripts/install-tools.mjs ../my-project --group browser --group context
```

第 1 步之后，**必须有人补全 `AGENTS.md` 里的 `TODO` 段落** —— 规范不填满，装出来的只是空壳。

## 设计原则

| 原则 | 含义 |
|---|---|
| **模板 + 安装，而非拷贝** | 同一套能力能装到不同技术栈的项目；占位符保证路径真实可用 |
| **配置进仓库，不进个人机器** | MCP、skills、脚本都写进项目配置，换机器 clone 就能跑 |
| **规范是事实，不靠口头** | `AGENTS.md` / `docs/standards/` 是唯一权威，冲突以文件为准 |
| **AI 执行，人决策** | Plan 的人工确认是唯一强制闸门；范围、需求、规范的变更必须人拍板 |
| **幂等可重入** | 所有安装脚本可重复执行，默认不覆盖已有文件 |

## 目录结构

```
team-harness-suite/
├── AGENTS.md             # 本仓库的架构与工程规范（改代码前先读）
├── agile-team-sdd/       # SDD 技能套件（17 个模板 + catalog.json + 安装脚本）
├── harness-installer/    # AGENTS.md / docs 骨架初始化
├── tool-chain-installer/ # MCP 工具链安装
├── team-workflow-guide/  # 团队流程与角色手册
├── overnight-runner/     # 无人值守跑 plan 的分屏面板 + 看门狗
├── example-project/      # 全栈参考实现（已装全套 skills）
├── .agents/
│   ├── verify.sh         # 一键验证
│   ├── plan/             # 本仓库开发计划
│   └── skills/           # 维护型：work-in-example / modify-example / modify-harness
└── opencode.jsonc        # 注册本仓库的 skills 路径
```

## 开发

```bash
./.agents/verify.sh          # 全量验证
./.agents/verify.sh --fast   # 跳过冒烟测试
```

工程约定见 [`AGENTS.md`](AGENTS.md) —— 改任何脚本前先读它。

## 状态

| 模块 | 状态 |
|---|---|
| `agile-team-sdd/` | ✅ 可用（17 个 skill） |
| `harness-installer/` | ✅ 可用（`AGENTS.md` 模板含 TODO，需人工补全） |
| `tool-chain-installer/` | ✅ 可用 |
| `team-workflow-guide/` | ✅ 可用 |
| `overnight-runner/` | ✅ 可用（面板 / 看门狗 / 多队列 / 决策记录 / 决策窗口） |
| `example-project/` | ✅ 完整可跑 |

## License

见 [LICENSE](LICENSE)。
