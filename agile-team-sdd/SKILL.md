---
name: agile-team-sdd
description: 安装 Agile Team SDD 技能套件（16 个 skill，覆盖 BA/开发/QA/PM 全流程）到指定项目。当用户说"安装 skills 到某个项目"、"把 SDD 流程装到 X 仓库"、"agile team sdd 安装"时使用。
---

# Agile Team SDD：安装技能套件

本目录是 **SDD（Spec-Driven Development）技能套件的模板源**。
`skills/` 下每个子目录是一份带占位符的 `SKILL.md`，需要先渲染成目标项目的真实路径，再安装过去。

## 技能清单（16 个）

完整元数据见 [`catalog.json`](catalog.json)。

### BA — 业务分析

| Skill | 作用 | 触发时机 |
|---|---|---|
| `ba-grill-me` | 拷问需求，把模糊描述逼成可验收的规格 | 需求含糊、有多种理解时，写规格之前 |
| `ba-write-spec` | 编写需求规格（字段表、业务规则、权限、验收标准） | 需求已澄清，落成 `docs/features/<迭代>/<CODE>-<slug>/spec.md` |
| `ba-gen-facts` | 从代码生成/校准事实文档（API、库表、领域模型） | 实现变了，`docs/facts/` 与代码不一致 |

### 开发

| Skill | 作用 | 触发时机 |
|---|---|---|
| `dev-plan` | 在 feature 目录写 `plan.md` 再动手 | 新功能 / 重构 / 非简单变更 |
| `dev-build` | 按四层 DDD 约定实现功能 | Plan 已确认，进入实现 |
| `dev-self-test` | 运行并修复开发自测 | 实现完成、交给 QA 之前 |
| `dev-code-review` | 按项目规范做代码评审 | 提交前自查，或评审别人的 MR |
| `dev-ui-review` | 用 chrome-devtools-mcp 做界面评审 | 前端需要实机检查 |
| `dev-release-plan` | 整理当前迭代上线准备清单 | 迭代收尾，准备发版 |
| `dev-create-mr` | 创建 Merge Request / Pull Request | 自测通过，准备提交评审 |

### QA

| Skill | 作用 | 触发时机 |
|---|---|---|
| `qa-write-cases` | 编写 QA 用例（`TC-xxx` 文本 + 自动化） | 规格已确认，把验收标准变成用例 |
| `qa-run-e2e` | 运行 E2E 用例集并定位失败 | 验收前，或用例失败排查 |
| `qa-write-manual-plan` | 编写手动测试与冒烟用例计划 | 自动化覆盖不到的场景 / 发版前 |

### PM

| Skill | 作用 | 触发时机 |
|---|---|---|
| `pm-estimate` | 基于需求分类基线表估算工作量 | 需求进迭代前 |
| `pm-retro` | 复盘并把改进项回写到 harness 本身 | 迭代结束，或流程反复出问题 |

### 全流程串起来

```
需求
 └─ ba-grill-me ──▶ ba-write-spec ──▶ pm-estimate
                                          │
                              qa-write-cases│
                                          ▼
                       dev-plan ──▶ dev-build ──▶ dev-self-test
                                          │              │
                                          ▼              ▼
                                     ba-gen-facts    dev-code-review / dev-ui-review
                                                          │
                                                          ▼
                                                     dev-create-mr
                                                          │
                                     qa-write-manual-plan / qa-run-e2e
                                                          │
                                                          ▼
                                                    dev-release-plan
                                                          │
                                                          ▼
                                                        pm-retro ──▶ 改进 harness
```

## 安装步骤

### 1. 确认目标项目

必须先确定 **目标项目目录**（绝对路径）。如果用户没有说清楚，用 `question` 工具问清楚，
不要默认装到当前目录。

### 2. 执行安装脚本

```bash
# 从本 skill 所在目录执行
./agile-team-sdd/install.sh <目标项目目录>
```

常用参数：

| 参数 | 说明 |
|---|---|
| `--list` | 列出全部可用 skill 并退出 |
| `--group <g>` | 只安装某一组（`ba` / `dev` / `qa` / `pm`），可重复 |
| `--skill <name>` | 只安装指定 skill，可重复 |
| `--dry-run` | 只打印将要发生的改动，不写文件（推荐先跑一次） |
| `--force` | 覆盖目标项目里已存在的同名 skill |
| `--no-config` | 不修改目标项目的 `opencode.jsonc` |

环境变量：

| 变量 | 说明 |
|---|---|
| `PATH_MODE=relative` | 渲染成项目相对路径而不是绝对路径（项目要随仓库分发给别人的时候用） |
| `HARNESS_ROOT` | 套件源码根目录（`pm-retro` 回写用，默认取安装脚本所在套件的根） |
| `BACKEND_DIR` / `FRONTEND_DIR` / `DOCS_DIR` / … | 覆盖目录推断，见 [placeholders.md](placeholders.md) |

脚本会做五件事：

1. 把 `skills/<name>-template/**` 渲染（替换 `{{...}}` 占位符、删除 TEMPLATE-ONLY 标记块、把 `name` 去掉 `-template` 后缀）
2. 整个模板目录写入 `<目标项目>/.agents/skills/<name>/`（附属文件如 `baseline.md` 一并渲染）
3. 在目标项目的 `opencode.jsonc` 里注册 `skills.paths = [".agents/skills"]`（已存在则不覆盖）
4. 检查是否还有未替换的占位符并报警
5. 输出安装/跳过清单

### 3. 校验

安装后确认：

- 目标项目 `.agents/skills/` 下每个 `SKILL.md` 里 **不再有** `{{...}}`
- 目标项目 `opencode.jsonc` 的 `skills.paths` 指向 `.agents/skills`
- 提示用户 **重启 opencode** 后 skill 才会生效

## 路径约定

默认按下面的目录布局推断，也可用同名环境变量覆盖：

```
<项目根>/
├── AGENTS.md            ← {{AGENTS_FILE}}
├── .agents/skills/       ← {{SKILLS_DIR}}
├── .mcp.json            ← {{MCP_CONFIG_FILE}}
├── apps/
│   ├── backend/         ← {{BACKEND_DIR}}
│   └── frontend/        ← {{FRONTEND_DIR}}
├── e2e/                 ← {{E2E_DIR}}
├── e2e-run.sh           ← {{E2E_RUNNER}}
└── docs/
    ├── features/        ← {{FEATURES_DIR}}
    │   ├── _chores/     ← {{CHORES_DIR}} / {{PLANS_DIR}}
    │   └── _template/   ← {{SPEC_TEMPLATE}} / {{PLAN_TEMPLATE}}
    ├── facts/           ← {{FACTS_DIR}}
    │   ├── business/    ← {{BUSINESS_FACTS_DIR}}
    │   └── tech-topic/  ← {{TECH_TOPIC_DIR}}
    ├── standards/       ← {{STANDARDS_DIR}}
    ├── test-cases/
    │   ├── e2e-cases/       ← {{E2E_CASES_DIR}}
    │   ├── manual-cases/    ← {{MANUAL_CASES_DIR}}
    │   ├── smoking-cases/   ← {{SMOKING_CASES_DIR}}
    │   └── dev-self-cases/  ← {{DEV_SELF_CASES_DIR}}
    └── releases/        ← {{RELEASES_DIR}}
```

完整占位符字典见 [`placeholders.md`](placeholders.md)。

## 注意

- 安装是 **拷贝**，不是软链：目标项目里的 skill 是渲染后的独立副本，之后两边各自演进。
  升级模板后要重新执行 `install.sh --force`。
- 模板文件本身也会被 opencode 扫描到（它们在 `skills.paths` 里）。模板描述里含 `{{...}}`，
  是有意为之——识别到未渲染模板时，应当 **先执行安装** 而不是照着模板里的路径干活。
- 模板 skill 名带 `-template` 后缀（`dev-plan-template`），安装后去掉后缀（`dev-plan`），
  这样模板与已安装的 skill 不会重名冲突。
- `pm-retro` 会回写套件源码，路径由 `{{HARNESS_ROOT}}` 给出（安装时自动填入）。
- 目标项目如果没有 `AGENTS.md` / `docs/`，请先运行 `harness-installer` skill 初始化。
