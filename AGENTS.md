# 架构与工程规范（team-harness-suite）

本文件定义本仓库的架构边界、模块职责与工程规范。目标是让新成员与自动化工具在不了解上下文的情况下，
也能按一致方式新增模块、扩展能力并避免破坏依赖关系。

> 这是一个 **harness 仓库**，不是业务应用。仓库里没有运行时服务，
> 交付物是 **skill、安装脚本、模板、文档** —— 它们被安装到别人的项目里去干活。
>
> 参考实现在 [`example-project/`](example-project/)：一份填满规范的全栈项目，
> 用来说明"被这套 harness 管理之后，项目应该长什么样"。

## 1. 仓库拓扑

技术栈：

| 类型 | 技术 | 用在哪 |
|---|---|---|
| 文档 | Markdown | skill、指南、规范、模板 |
| 脚本 | Bash 3.2+ | 安装脚本（安装器型 skill） |
| 脚本 | Python 3.9+（**零第三方依赖**） | `overnight-runner` 与 `agents-workflow-engine` |
| 脚本 | Node.js 18+ | `tool-chain-installer` 的安装器 |
| 配置 | YAML | 队列配置、项目配置、skill 清单 |
| 配置 | JSON / JSONC | MCP 工具清单、opencode 配置 |

主要模块：

```
team-harness-suite/
├── .agents/              # 本仓库自用：verify.sh + plan/ + skills/
├── agile-team-sdd/       # SDD 技能套件（26 个 skill 模板 + 安装器）
├── harness-installer/    # 初始化目标项目的 AGENTS.md + docs/ 骨架
├── tool-chain-installer/ # 安装 MCP 工具链到项目配置
├── overnight-runner/     # 无人值守跑 plan 的分屏面板 + 看门狗
├── agents-workflow-engine/ # 主会话按泳道图调度子 agent，到人工补测为止
├── team-workflow-guide/  # 团队流程与角色手册（纯文档）
├── example-project/      # 全栈参考实现（被这套 harness 管理的样子）
└── opencode.jsonc        # 注册本仓库的 skills 路径
```

运行时形态：

```
使用者 ──安装──▶ 目标项目 ──▶ opencode 加载 skill
                                  │
                                  ├─ agile-team-sdd      → 目标项目/.agents/skills/
                                  ├─ harness-installer   → 目标项目/AGENTS.md + docs/
                                  ├─ tool-chain-installer→ 目标项目/.mcp.json + opencode.jsonc
                                  └─ overnight-runner    → 目标项目/.overnight-runner/
```

## 2. 横切关注点：skill 机制与占位符

本仓库的 **核心机制** 是 skill。所有模板型交付物都遵守同一套约定。

### skill 的四种形态

| 形态 | 目录 | 干什么 |
|---|---|---|
| **安装器型** | `harness-installer/`、`tool-chain-installer/` | 一个 skill，作用是把东西装进目标项目 |
| **套件型** | `agile-team-sdd/` | 一个 skill（安装器）+ N 个 skill 模板，一次装一批 |
| **运行时型** | `overnight-runner/` | Python 运行时 + 安装脚本；**Agent skill** 在 `agile-team-sdd`（无前缀 `overnight-runner`） |
| **维护型** | `.agents/skills/` | 本仓库自用：`work-in-example`（样例上下文）与 example↔harness 刷新（不装进目标项目） |
| **文档型** | `team-workflow-guide/` | 不是 skill，是人读的指南 |

### SKILL.md 格式（强制）

```markdown
---
name: <与所在目录同名，小写连字符，≤64 字符>
description: <一句话说明"做什么"+"什么时候用"，第三人称，前置触发关键词>
---

<正文：什么时候用 / 怎么做 / 硬性约束 / 反模式 / 自检清单>
```

- `name` **必须** 与目录名一致 —— opencode 靠它索引
- `description` 是 **唯一** 的触发依据，写得含糊 skill 就等于不存在
- 正文里的路径 **不能** 写死成某个项目的绝对路径

### 占位符（强制）

模板里的项目专属路径一律写成 `{{PLACEHOLDER}}`，由安装脚本渲染：

```
{{PROJECT_ROOT}}   {{FEATURES_DIR}}   {{FACTS_DIR}}   {{AGENTS_FILE}}   ...
```

约束：

- 占位符字典写在 `agile-team-sdd/placeholders.md`，**新增必须同步登记**
- 未登记的占位符会在安装时报警（`install.sh` 的残留检查）
- 渲染后的路径默认是绝对路径（`PATH_MODE=absolute`）；
  会随仓库分发的项目用 `PATH_MODE=relative`
- 占位符 **不替换** 与项目无关的内容（Markdown 代码块、语言标注、PlantUML 的 `{字段}`）

### 模板 skill 的命名

模板目录带 `-template` 后缀，安装时去掉：

```
agile-team-sdd/skills/dev-plan-template/SKILL.md   （frontmatter: name: dev-plan-template）
        ↓ install.sh
<目标项目>/.agents/skills/dev-plan/SKILL.md           （frontmatter: name: dev-plan）
```

**原因**：模板本身也要能被 opencode 扫描到，但不能和已安装的同名 skill 冲突。

### 模板标记块

每份模板 `SKILL.md` 顶部带：

```markdown
<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记……
<!-- /TEMPLATE-ONLY -->
```

安装时整块删除。**新增模板必须带这个块**，否则安装后会出现"这是模板"的提示。

## 3. 模块边界

```
        ┌─────────────────┐
        │ team-workflow-  │  流程与角色约定（人读）
        │    guide/       │
        └────────┬────────┘
                 │ 指导
   ┌─────────────┼─────────────┐
   │             │             │
┌──▼──────────┐ ┌▼───────────┐ ┌▼──────────────────┐
│harness-     │ │agile-team- │ │tool-chain-        │
│installer/   │ │sdd/       │ │installer/         │
│AGENTS.md    │ │26 个 skill │ │MCP 工具链          │
│docs/ 骨架    │ │模板 + 安装器│ │                   │
└─────────────┘ └┬───────────┘ └──────────────────┘
                 │ 装进
        ┌────────▼─────────┐
        │ example-project/ │  参考实现
        └──────────────────┘

        ┌──────────────────┐
        │ overnight-runner/│  运行时；skill 由 agile-team-sdd 下发
        └──────────────────┘
```

硬约束：

- **四个安装器/套件型模块之间不互相 import**。它们通过 **文件系统与 YAML 清单** 通信。
  唯一允许的跨模块引用是 **文档里的路径**。
- `example-project/` 是 **被管理的对象**，不是本仓库的实现的一部分。
  它的代码不参与本仓库的验证脚本（除了 skill 一致性检查）。
- `team-workflow-guide/` 是 **纯文档**，不包含可执行代码。

## 4. 清单是唯一事实源

每个可扩展的集合都有 **一份清单**，其它地方不许硬编码：

| 集合 | 清单文件 | 谁读它 |
|---|---|---|
| SDD skill 套件 | `agile-team-sdd/catalog.json` | `install.sh`（分组过滤）、`SKILL.md`（文档） |
| MCP 工具 | `tool-chain-installer/catalog/mcp-catalog.json` | `install-tools.mjs` |

`catalog.json` 的每一项至少包含：

```json
{
  "name": "dev-plan",
  "description": "在实现前写技术方案（Plan），等待人工确认",
  "when": "新功能、重构或任何非简单变更，动手写代码之前",
  "produces": ["docs/features/<迭代>/<CODE>-<slug>/plan.md"],
  "dependsOn": []
}
```

**新增 skill 的完整流程**：建 `skills/<name>-template/SKILL.md` → 在 `catalog.json` 登记 →
跑 `install.sh --list` 验证 → 补 `agile-team-sdd/SKILL.md` 与 `README.md` 的表格。

## 5. 文件与目录约定

### 脚本

| 位置 | 用途 | 入口约定 |
|---|---|---|
| `<模块>/scripts/install.sh` | 安装到目标项目 | `./install.sh <目标目录> [--dry-run] [--force]` |
| `<模块>/scripts/*.mjs` | Node 安装器 | `node <script>.mjs <目标目录> [选项]` |
| `overnight-runner/overnight_runner/` | Python 实现 | `python -m overnight_runner <子命令>` |

约束：

- 脚本 **必须** 有 `--help` / `--dry-run`
- 脚本 **必须** 幂等：重复执行不产生副作用，默认不覆盖已有文件
- 脚本 **必须** 能在没有目标文件的情况下自己创建
- 路径处理用 `$(cd "$(dirname "$0")/.." && pwd)` 定位自身，不依赖 cwd

### Python（仅 `overnight-runner`）

- 3.9+ 兼容（不用 `match`、`X | Y` 类型语法）
- **零第三方依赖** —— 只用标准库。界面用 `term.py` 自绘 ANSI，
  配置用 `yaml_lite.py` 自实现 YAML 子集。**不引入任何 pip 包**
- 模块划分：
  `cli / config / yaml_lite / queue / prompts / decisions / agent / controller / keys / ui / term / util`
- 数据流单向：`ui → controller → (queue, agent, decisions, prompts)`，
  **底层模块不反向 import 上层**
- 跨平台：按键读取 POSIX 用 `termios`、Windows 用 `msvcrt`；
  进程终止 POSIX 用 `killpg`、Windows 用 `CREATE_NEW_PROCESS_GROUP`
- 自绘界面时，宽度计算必须 **忽略 ANSI 转义序列**（否则带颜色的文本会把边框挤歪）；
  中日韩字符按 `east_asian_width` 算 2 列

### Markdown

- 文档标题用中文，代码/标识符用英文
- 表格用于对比，列表用于步骤，**不要** 用大段散文描述流程
- 每个模块目录有 `README.md`，说明"是什么 / 怎么用 / 维护时改哪"
- 文档里的相对链接必须有效（验证脚本会检查）

## 6. 安装脚本的幂等与安全

所有安装器遵守同一套约定：

| 约定 | 说明 |
|---|---|
| 默认不覆盖 | 已有文件跳过并提示，需要覆盖时显式 `--force` |
| 先 `--dry-run` | 预览要做什么，再真跑 |
| 原子写 | 配置文件用「临时文件 + rename」，避免读到写了一半的内容 |
| 不写绝对路径到产物 | 安装到目标项目的文件里 **不能** 出现安装机的路径 |
| 不碰目标项目的业务代码 | 只写自己约定的文件（`.agents/skills/`、`docs/`、配置文件…） |
| 密钥不落盘 | 需要密钥的配置写 `{env:VAR}` 引用，真值由使用者注入 |

## 7. 错误处理

| 层 | 约定 |
|---|---|
| Bash 脚本 | `set -euo pipefail`；错误信息写到 stderr 并以非零退出；对用户可见的错误用中文 |
| Python | 抛异常并给出 **可操作的** 消息（含路径、原因、怎么办）；不用裸 `except:` |
| Node | `process.exit(1)` + stderr；不吞异常 |
| CLI | 子命令返回退出码：0 成功，1 有失败，2 环境/依赖缺失，130 被中断 |

原则：**用户看得见的失败必须说清楚是哪一步、为什么、怎么继续**，
不要只留一个堆栈。

## 8. 模块职责

| 模块 | 职责 | 不负责 |
|---|---|---|
| `agile-team-sdd/` | SDD 流程 skill 的 **模板源** 与安装器 | 不实现具体流程细节（那是各 skill 的正文） |
| `harness-installer/` | 铺 `AGENTS.md` + `docs/` 骨架 | 不填 `AGENTS.md` 里的 TODO（那是人填的） |
| `tool-chain-installer/` | 装 MCP 工具链 | 不装 npm/pip 依赖 |
| `overnight-runner/` | 无人值守跑 plan 的运行时 | 不判断 plan 质量（人的责任） |
| `agents-workflow-engine/` | 主会话按泳道图调度子 agent，跑到人工补测 | 不实现 QA 流水线本身（由对应 skill 负责），不拆 `dev-build` 内部六步 |
| `team-workflow-guide/` | 流程与角色约定 | 不含可执行代码 |
| `example-project/` | 参考实现 | 不参与本仓库的验证脚本 |

### 数据流

```
项目准备：tl-arch-plan（BA/TL）→ docs/architecture/（C4、ADR、术语、领域意图、迭代规划）
用户的一句话需求
  → ba-grill-me（拷问）
  → ba-write-spec（需求规格 docs/features/<迭代>/<CODE>-<slug>/spec.md；术语 → architecture/business/glossary.md）
  → pm-estimate（估算）
  → ┬─ tl-high-level-design（迭代 high-level-design.md，人工确认 ← Plan 前强制闸门）
    └─ qa-write-cases（QA 文本用例，与 HLD 并行；规格确认后即可开始）
  → HLD 确认后 → dev-plan（技术方案 feature/plan.md 或 _chores/，人工确认 ← 编码前强制闸门）
  → Plan 确认后 → dev-build（实现 → self-test 真实环境+DST 落盘 → ui-review 原型对照落盘 → code-review；以记录为准修到绿）
  → ba-gen-facts（事实文档 docs/facts/ 同步）
  → tl-arch-sync-back / ba-arch-sync-back（architecture ↔ 实现/规格漂移时）
  → dev-create-mr
  → qa-run-e2e / qa-write-manual-plan（QA 验收，合并闸门）
  → dev-release-plan（上线清单 docs/releases/）
  → pm-retro（复盘 → 回写 harness 本身）
```

## 9. 状态机

### skill 生命周期

```
模板 skills/<name>-template/SKILL.md
   │ install.sh（渲染占位符 + 去 -template 后缀 + 删 TEMPLATE-ONLY 块）
   ▼
已安装 <目标项目>/.agents/skills/<name>/SKILL.md
   │ opencode 重启后加载
   ▼
可被触发
   │ 模板升级
   ▼
install.sh --force（重新渲染覆盖）
```

**配置改动不热更新** —— 改完 skill / MCP 配置必须重启 opencode。

### 任务状态机（`overnight-runner`）

```
pending ──▶ running ──┬──▶ success
   ▲          │        ├──▶ retrying ──▶ running   （退避后重试）
   │          │        ├──▶ failed
   │          │        └──▶ blocked
   └──────────┴── （面板 r 键重置）
```

### 决策来源（`overnight-runner`）

| source | 含义 |
|---|---|
| `agent` | agent 自己按默认决策做完了，输出了 `DECISION:` |
| `rule` | agent 抛 `QUESTION:`，命中预设规则 |
| `fallback` | 没命中任何规则，用 `onUnknownDecision` 兜底 |
| `human` | 人在 TUI 决策窗口里回答的（`attended` 模式） |
| `timeout` | 决策窗口等超时，自动兜底的（`attended` 模式） |

五种都写进 `decisions.jsonl`（**per-queue**），用于事后回溯。

### 决策模式（`overnight-runner`）

按"有没有人盯着"分两种：

| mode | 行为 |
|---|---|
| `attended`（白天有人值守） | agent 抛 `QUESTION:` → **打断 agent**，TUI 弹带倒计时的决策窗口；人答（`Enter`）就用 `agent --session <sid>` 续跑；超时没人答就按规则/兜底策略自动决策 |
| `unattended`（夜里无人值守） | 不打断 agent，按规则/兜底策略直接决策；决策在下次拉起 agent 时注入 prompt |

- 决策窗口默认 **600 秒**（`runner.decision.timeoutSec`）
- `--headless` **强制** `unattended`（没人看面板，不能卡在等决策上）
- `run --mode attended|unattended` 可临时覆盖配置文件
- 队列目录 `.overnight-runner/queue/<name>/` —— 一条队列一个目录，多人各跑各的；
  同一条队列有 `.lock` 单实例锁，不许两个 runner 同时跑

## 10. 测试规范

### 本仓库的验证

本仓库没有单元测试套件，靠 **静态检查 + 集成冒烟**：

| 检查 | 命令 |
|---|---|
| Bash 语法 | `bash -n <file>` |
| Python 语法 | `python -m py_compile <file>` |
| Node 语法 | `node --check <file>` |
| JSON / YAML 可解析 | 解析一遍 |
| skill 名/目录一致、无重名 | 见验证脚本 |
| 清单 ↔ 模板 ↔ 已安装 三方一致 | 见验证脚本 |
| Markdown 相对链接有效 | 见验证脚本 |
| 安装后无残留占位符 | 见验证脚本 |
| overnight-runner 单元测试 | `overnight-runner/tests/test_units.py`（44 个用例：YAML 子集 + 终端宽度 + 队列路径/迁移 + 决策 + 锁 + 按键读取） |
| overnight-runner 行为 | `overnight-runner/tests/test_smoke.py`（13 个用例，假 agent 驱动） |

一条命令跑全部：

```bash
./.agents/verify.sh
```

**改了任何脚本都要跑。** 改 overnight-runner 的行为要额外跑冒烟测试。

### `overnight-runner` 的测试规范

- 用 **假 agent 脚本**（临时 bash 文件）驱动，不用真实 agent
- 每个用例一个独立临时目录
- 覆盖：成功+决策记录、失败重试到上限、空闲超时杀进程、`QUESTION` 命中规则、
  队列追加 id 去重、agent 输出解析、规则匹配、
  **有人值守人回答后 session 续跑**、**有人值守超时兜底**、**决策历史注入**、
  **无人值守不打断**、**headless 强制无人值守**、**`--mode` 覆盖**、
  **中文按键原样读出**、**汉字被拆到两次读里仍能还原**
- 假 agent 要 **记录每次调用的命令行**（断言"续跑时带了 `--session`"要用）
- 断言要具体（状态、重试次数、记录内容），不要只断言"没崩"

### `example-project` 的测试

那是它自己的事，见 `example-project/AGENTS.md` §10。
**本仓库的验证脚本只对它做静态检查**（语法、配置可解析、skill 一致性），
不跑它的测试（`mvn test` 需要 MySQL，Playwright 需要 npm install）。

## 11. 界面规范（`overnight-runner` 的面板）

分屏：左边任务队列，右边 agent 输出。

| 规范 | 说明 |
|---|---|
| 布局 | `term.py` 自绘：左列固定宽度（`LEFT_WIDTH`），右列占满剩余 |
| 全屏 | `ESC[?1049h` 进备用屏幕缓冲区，退出时恢复终端 |
| 刷新 | `refreshHz` 控制（默认 8），不追求高帧率 |
| 按键 | 独立线程读（`KeyReader`），不阻塞渲染循环 |
| 追加 plan | **行内输入模式**（按 `a` 进入，`Enter` 确认，`Esc` 取消），不用弹窗 |
| 决策窗口 | 右栏抢占，显示问题 + 输入框 + 倒计时；`Enter` 提交 · `Esc` 兜底 · `Ctrl-C` 退出；按键优先级高于追加 plan |
| 按键读取 | 必须按 **UTF-8 字节凑齐再解码**（一次读 1 字节会把汉字拆成乱码）；ESC 序列在缓冲区里判定，不额外读 |
| 右栏标题 | 用 **正在跑** 的任务（`_running_task()`），不是选中行 —— 否则切行后标题与内容对不上 |
| 颜色 | 状态用固定语义色（成功绿 / 失败红 / 运行青 / 重试黄） |
| 无 TTY | 必须能降级：`--headless` 走纯 stdout；`Term` 检测到非 TTY 时不输出任何转义序列 |

改界面时保持 **键盘操作不依赖鼠标**。

## 12. PR / 变更检查清单

- [ ] `SKILL.md` 的 `name` 与目录名一致，`description` 说清了"什么时候用"
- [ ] 新增 skill 已在 `catalog.json` 登记，并补进 `agile-team-sdd/SKILL.md` 与 `README.md` 的表格
- [ ] 新增占位符已在 `placeholders.md` 登记
- [ ] 模板 `SKILL.md` 带 `TEMPLATE-ONLY` 标记块
- [ ] 安装脚本幂等：`--dry-run` 可跑，重复执行不炸
- [ ] 产物里 **没有** 安装机的绝对路径
- [ ] 跑过 `./.agents/verify.sh`
- [ ] 改了 `overnight-runner` 的行为 → 单元测试 44/44 + 冒烟测试 13/13 通过
- [ ] 文档里的相对链接有效
- [ ] 没提交 `.venv/`、`__pycache__/`、运行时状态（`.overnight-runner/queue/*/state.json`、`logs/`、`.lock`）

## 13. 文档结构

```
team-harness-suite/
├── README.md                     # 仓库总览：目的 + 模块表 + 快速开始
├── AGENTS.md                     # 本文件：架构与工程规范
├── opencode.jsonc                # 注册本仓库的 skills 路径
│
├── .agents/
│   ├── verify.sh                 # 一键验证
│   ├── plan/                     # 本仓库自身的开发计划（业务项目用 feature/plan 或 _chores）
│   └── skills/                   # 本仓库维护型 skill（work-in-example / modify-example / modify-harness）
│
├── agile-team-sdd/
│   ├── README.md                 # 套件说明
│   ├── SKILL.md                  # 安装 skill
│   ├── install.sh                # 安装脚本
│   ├── catalog.json              # skill 清单（唯一事实源）
│   ├── placeholders.md           # 占位符字典
│   └── skills/<name>-template/   # skill 模板
│
├── harness-installer/
│   ├── README.md
│   ├── SKILL.md
│   ├── scripts/init-harness.sh
│   └── templates/                # AGENTS.md 模板 + docs/ 骨架
│
├── tool-chain-installer/
│   ├── README.md
│   ├── SKILL.md
│   ├── scripts/install-tools.mjs
│   └── catalog/mcp-catalog.json
│
├── overnight-runner/
│   ├── README.md
│   ├── SKILL.md
│   ├── docs/design.md             # 设计说明与取舍
│   ├── scripts/install.sh
│   ├── config/*.example.yaml      # 配置样例
│   ├── overnight_runner/          # Python 实现
│   └── tests/{test_units,test_smoke}.py
│
├── team-workflow-guide/
│   ├── index.html                 # 主文档（HTML 单页：总览矩阵 + 三阶段 + 测试 + 角色）
│   └── README.md                  # 入口说明（指向 index.html）
│
└── example-project/               # 全栈参考实现（被管理的样子）
```

### 同步要求

- 改了某个 skill 的行为 → 同步 `agile-team-sdd/SKILL.md` 与 `README.md` 的表格
- 加了占位符 → 同步 `agile-team-sdd/placeholders.md`
- 加了 skill → 同步 `catalog.json` + `agile-team-sdd/SKILL.md` + `README.md` + 根 `README.md`
- 改了模块职责 → 同步本文件 §3 与 §8
- 改了流程 / 角色协作 / 测试分类 → 同步 `team-workflow-guide/index.html`；测试分类同时同步 `example-project/docs/standards/test.md`

### 执行检查点

每轮任务提交描述中必须包含：

- [ ] 文档同步检查（已更新 / 不涉及）

## 14. 开发流程（每轮需求的标准执行步骤）

每轮改动必须按以下顺序执行，严禁跳过或调换步骤：

1. **确认范围**：改动落在哪个模块？是加 skill、加占位符、改脚本，还是改文档？
2. **Plan 等待确认**：在 `.agents/plan/` 下按 `YYYYMMDD-{slug}.md` 写方案，等待人工确认后再继续。
   （本 harness 仓库用 `.agents/plan/` 保持根目录干净；目标/业务项目仍用 `docs/plans/`。）
3. **先写验证**：能加自动化检查的先加（验证脚本、冒烟用例），再写实现。
4. **编写实现**：按 §5 的文件与目录约定落代码，遵循 §3 的模块边界。
5. **运行验证**：`./.agents/verify.sh` 全绿；改了 overnight-runner 则冒烟测试全绿。
6. **同步文档**：按 §13 的同步要求逐条过。
7. **提交**：提交描述里写清楚「改了什么 / 为什么 / 怎么验证的 / 文档同步检查」。

> **AI Agent 注意**：目标/业务项目有两道强制闸门——迭代 `high-level-design.md`（`tl-high-level-design`）与 feature `plan.md`（`dev-plan`）。
> 本 harness 仓库自身仍用 `.agents/plan/`；不要自己写完 Plan 就接着写代码。
