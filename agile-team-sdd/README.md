# agile-team-sdd

SDD（Spec-Driven Development）技能套件的 **模板源**，覆盖 **BA → TL → PM → 开发 → QA → 发布 → 复盘** 全流程，
共 18 个 skill。

```
agile-team-sdd/
├── SKILL.md              # 安装 skill：把 skills/ 渲染并安装到指定项目
├── install.sh            # 安装脚本（渲染 + 落盘 + 注册 opencode 配置）
├── catalog.json          # 技能清单（分组 / 作用 / 触发时机 / 依赖）
├── placeholders.md       # 占位符字典
└── skills/
    ├── ba-grill-me-template/      # 拷问需求
    ├── ba-write-spec-template/    # 编写需求规格
    ├── ba-gen-facts-template/     # 生成事实文档
    ├── tl-high-level-design-template/ # 迭代高阶技术设计（HLD）
    ├── dev-plan-template/         # 先写计划再实现
    ├── dev-build-template/        # 按四层 DDD 约定实现
    ├── dev-self-test-template/    # 开发自测
    ├── dev-code-review-template/  # 代码评审
    ├── dev-ui-review-template/    # 界面评审
    ├── dev-release-plan-template/ # 上线准备清单
    ├── dev-create-mr-template/    # 创建 MR/PR
    ├── qa-write-cases-template/   # 编写 QA 用例
    ├── qa-run-e2e-template/       # 运行 E2E
    ├── qa-write-manual-plan-template/ # 手动与冒烟用例
    ├── pm-estimate-template/      # 工作量估算（附 baseline.md 基线表）
    ├── pm-retro-template/         # 复盘并改进 harness
    └── overnight-runner-template/ # 夜间/无人值守跑 plan（无角色前缀）
```

## 技能分组

| 组 | Skill | 作用 |
|---|---|---|
| **BA** | `ba-grill-me` | 拷问需求，把模糊描述逼成可验收的规格 |
| | `ba-write-spec` | 编写需求规格：字段表、业务规则、权限矩阵、验收标准；维护项目级术语表 |
| | `ba-gen-facts` | 从代码生成/校准事实文档：API、库表、领域模型、专题 |
| **TL** | `tl-high-level-design` | 写迭代高阶技术设计（HLD / TRD），确认前不得开 Plan |
| **Dev** | `dev-plan` | 实现前写技术方案，等待人工确认 |
| | `dev-build` | 全栈编排：实现 + 自测 / UI 评审 / 代码评审 |
| | `dev-self-test` | 开发自测（由 build 编排，可单跑） |
| | `dev-code-review` | 代码评审（由 build 编排，可单跑） |
| | `dev-ui-review` | chrome-devtools-mcp 界面评审（由 build 编排） |
| | `dev-release-plan` | 整理迭代上线准备清单 |
| | `dev-create-mr` | 创建 Merge Request / Pull Request |
| **QA** | `qa-write-cases` | 编写 QA 用例（`TC-xxx` 文本 + 自动化） |
| | `qa-run-e2e` | 运行 E2E 用例集并定位失败 |
| | `qa-write-manual-plan` | 编写手动测试与冒烟用例计划 |
| **PM** | `pm-estimate` | 基于需求分类基线表估算工作量 |
| | `pm-retro` | 复盘并把改进项回写到 harness |
| **Runner** | `overnight-runner` | 队列跑已确认 plan（多队列、看门狗、决策留痕；无角色前缀） |

## 为什么用占位符

模板不能写死 `docs/plans/`、`backend/` 这类 **项目专属路径**——套件要能装到不同技术栈的项目里。
所以模板中所有路径都写成 `{{PLACEHOLDER}}`，安装时由 `install.sh` 渲染成目标项目的绝对路径。

模板 skill 目录名带 `-template` 后缀，安装时去掉 —— 装进目标项目的是 `dev-plan` 而不是 `dev-plan-template`。
后缀的作用是让模板本身也能被 opencode 扫描到，同时不和已安装的同名 skill 冲突。

## 用法

```bash
# 列出全部
./agile-team-sdd/install.sh --list

# 预览全部
./agile-team-sdd/install.sh ../my-project --dry-run

# 安装全部
./agile-team-sdd/install.sh ../my-project

# 只装某一组
./agile-team-sdd/install.sh ../my-project --group qa

# 只装某几个 skill
./agile-team-sdd/install.sh ../my-project --skill dev-plan --skill qa-run-e2e

# 覆盖升级
./agile-team-sdd/install.sh ../my-project --force

# 渲染成相对路径（项目要随仓库分发给别人的时候）
PATH_MODE=relative ./agile-team-sdd/install.sh ../my-project
```

安装后目标项目会得到：

```
<目标项目>/.agents/skills/<name>/SKILL.md
```

以及 `opencode.jsonc` 中新增的：

```json
{ "skills": { "paths": [".agents/skills"] } }
```

## 目录约定

目录名可用环境变量覆盖，默认值见 [`placeholders.md`](placeholders.md)：

```bash
BACKEND_DIR=service PLANS_DIR=doc/plan ./install.sh ../my-project
```

## 维护

- 新增 skill：建 `skills/<name>-template/SKILL.md` → 在 `catalog.json` 登记 → 跑 `./install.sh --list` 验证
- 改基线表（`pm-estimate/baseline.md`）：改完用 `--skill pm-estimate --force` 重新下发
- 复盘产生的改进项：由 `pm-retro` 回写本目录，并重新下发到各项目

## 相关

- `harness-installer/` — 初始化目标项目的 `AGENTS.md` 与 `docs/` 骨架（装 skills 前应先跑它）
- `tool-chain-installer/` — 装 MCP 工具链（`dev-debug` / `dev-ui-review` 依赖 chrome-devtools-mcp）
- `team-workflow-guide/` — 团队角色与协作约定
