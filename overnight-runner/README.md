# overnight-runner

把一串 **plan** 交给 coding agent 无人值守地跑。左边是任务队列，右边是 agent 的实时输出。

```
┌── 任务队列 ─────────────┬── Coding Agent ──────────────────────────┐
│ ▶ 20261103-feature-a 运行中│ $ opencode run "…"                       │
│   20261103-bugfix    成功 │ DECISION: 是否执行数据库迁移？ → 先写回滚 │
│   20261103-docs      待跑 │ …                                        │
│                         │                                            │
│ 待跑 1 · 运行 1 · 成功 1 │ 最近决策                                   │
│                         │ 是否执行数据库迁移 → 先写回滚脚本           │
└─────────────────────────┴────────────────────────────────────────────┘
```

## 为什么

一次要跑好几个 plan，人守着点 `opencode run` 没人愿意干。这个工具把它变成 **配置 + 启动**：

| 原来 | 现在 |
|---|---|
| 守着终端一个个跑 | 队列里排好，启动就走 |
| 任务状态靠人记 | 左边面板实时看 |
| agent 卡死了没人知道 | 看门狗自动判定并重试 |
| 半夜替我做的决定没人知道 | 每条决策都记录，可回溯 |
| 换台机器跑不起来 | 装一次，配置进仓库 |
| 几个人抢同一个队列 | 一人一条队列，状态互不串 |
| 白天 agent 卡在提问上没人管 | 弹决策窗口问你，超时自动兜底 |

## 安装

```bash
# 装到当前项目
./scripts/install.sh .
```

**零依赖**：只用 Python 3.9+ 标准库，不需要 `pip install`。

装完项目里会有：

```
<项目>/
└── .overnight-runner/
    ├── overnight-runner.yaml          # 运行配置（提交进仓库，全队列共享）
    ├── project.yaml                   # 项目配置：默认提示词 + 默认决策（提交）
    ├── overnight-runner               # 启动脚本（POSIX）
    ├── overnight-runner.cmd           # 启动脚本（Windows）
    ├── overnight_runner/              # 实现
    └── queue/
        └── default/                   # 一条队列一个目录
            ├── queue.yaml             # 队列定义：跑哪些 plan（提交）
            ├── state.json             # 运行时状态（不提交）
            ├── decisions.jsonl        # 决策记录（提交，便于回溯）
            ├── logs/                   # 每个任务的 agent 日志（不提交）
            └── .lock                   # 单实例锁（不提交）
```

**多队列**：`.overnight-runner/queue/<队列名>/` —— 同一个仓库里可以有多条队列，
多人各跑各的互不干扰（`--queue <名字>` 切换）。

**老项目自动迁移**：根目录旧的 `overnight-runner.yaml` 会迁入 `.overnight-runner/`；
队列写在 yaml `queue:` 段、状态在 `.overnight-runner/state.json` 的老布局，
第一次运行时 **自动搬到** `.overnight-runner/queue/default/`，不丢任务、不丢状态，且迁移幂等。

**依赖**：**没有**。

| 原本要什么 | 现在怎么做 |
|---|---|
| `rich` 画分屏 | `term.py` 自绘 ANSI（备用屏幕、光标定位、边框、语义色） |
| `PyYAML` 读配置 | `yaml_lite.py` 自实现 YAML 子集（缩进映射/序列、块标量、流式集合、注释） |

按键读取 POSIX 用 `termios`、Windows 用 `msvcrt`，进程终止 POSIX 用 `killpg`、
Windows 用 `CREATE_NEW_PROCESS_GROUP` —— 全是标准库。
**Windows / macOS / Linux 都支持**，而且不用装任何东西。

## 用法

```bash
OR=.overnight-runner/overnight-runner

$OR init                                   # 初始化配置
$OR add docs/plans/20261103-feature-a.md  # 追加 plan（相对项目根）
$OR add docs/plans/xxx.md --role QA --priority 20
$OR list                                   # 看队列
$OR status                                 # 看状态
$OR queues                                 # 看所有队列
$OR run                                    # 启动分屏面板
$OR run --headless                         # 无界面（CI / 脚本）
$OR run --headless --retry-failed          # 把上次失败的重新排一遍
$OR run --mode unattended                   # 临时切成无人值守（默认按配置）
$OR decisions                              # 看决策记录
$OR decisions --json                       # 决策记录（JSON）
```

### 多队列（多人各跑各的）

所有子命令都支持全局参数 `--queue <名字>`（默认 `default`）：

```bash
$OR --queue alice add docs/plans/alice-feature.md   # 排到 alice 队列
$OR --queue bob   add docs/plans/bob-feature.md     # 排到 bob 队列
$OR queues                                         # 一屏看清有几条队列、各自什么状态
$OR --queue alice run                              # 跑 alice 队列
```

每条队列的状态、日志、决策记录完全隔离（各自的目录），但 **默认决策规则是项目级共享** 的
（都在 `.overnight-runner/project.yaml`）—— 规则是"这个项目怎么做决定"，
决策 **记录** 才是"这条队列发生过什么"。

同一条队列 **不能同时跑两个 runner**（会白烧 agent），第二个会被挡住并退出（退出码 2）。

### 决策模式：白天有人值守 / 夜里无人值守

| | `attended`（白天有人值守） | `unattended`（夜里无人值守） |
|---|---|---|
| agent 提问时 | **打断 agent**，TUI 弹决策窗口 | 不打断，agent 继续跑 |
| 谁来决策 | 人（600 秒内）→ 超时自动兜底 | 规则 → `onUnknownDecision` 兜底 |
| 决策记录 source | `human` / `timeout` | `rule` / `fallback` |
| 决策能否被 agent 看到 | 能（续跑时直接带上） | 能（下次拉起时注入 prompt） |

配置在 `overnight-runner.yaml` 的 `runner.decision`：

```yaml
runner:
  decision:
    mode: attended        # attended（有人值守） | unattended（无人值守）
    timeoutSec: 600       # attended 模式下决策窗口等多久（秒）；0 = 不限
    resume: session       # session（续跑同一会话） | restart（重跑任务）
```

命令行可以临时覆盖（不改配置文件）：

```bash
$OR run --mode attended     # 白天：有人盯着，弹窗问人
$OR run --mode unattended   # 夜里：直接决策，不打扰
```

**`--headless` 强制 `unattended`** —— 没人看面板，不该卡在等 600 秒上。

### 决策窗口

agent 抛出 `QUESTION:` 时，右栏弹出带倒计时的决策框：

```
◆ 待决策
  任务: 20261106-fix-public-endpoints

  扩范围改还是先修 Bug？

  你的决策：
  > 先修 Bug，不要扩大改动范围▏

  剩余 9:58   Enter 确认 · Esc 用默认决策 · Ctrl-C 退出
```

| 键 | 作用 |
|---|---|
| `Enter` | 提交你的答案，agent 用 `--session` 续跑（上下文不丢） |
| `Esc` | 立刻放弃回答，按默认决策兜底 |
| `Ctrl-C` | 退出 runner |

超时（`timeoutSec` 到点）还没人回答 → 自动按规则/兜底策略决策，agent 续跑，**不会卡住队列**。

### 面板操作

| 键 | 作用 |
|---|---|
| `↑` `↓` | 选择任务 |
| `a` | 追加 plan（就地输入路径，回车确认） |
| `r` | 重置选中任务为待跑 |
| `p` | 暂停 / 恢复 |
| `d` | 移除 |
| `Enter` | 看选中任务的完整日志 |
| `Esc` | 返回实时输出 |
| `c` | 清屏 |
| `q` | 退出 |

决策窗口出现时（`attended` 模式），按键被决策框独占：`Enter` 提交 · `Esc` 用默认决策 · `Ctrl-C` 退出。

## 三层配置

| 层 | 文件 | 作用域 | 管什么 |
|---|---|---|---|
| runner 级 | `.overnight-runner/overnight-runner.yaml` | 项目 | agent、看门狗、UI、决策策略 |
| project 级 | `.overnight-runner/project.yaml` | 项目（全队列共享） | 默认提示词、默认决策规则 |
| queue 级 | `.overnight-runner/queue/<n>/queue.yaml` | 单条队列 | 跑哪些 plan |

### 1. 运行配置 `.overnight-runner/overnight-runner.yaml`

管 **怎么跑**。

```yaml
runner:
  agent:
    command: opencode          # 或 claude / codex / 任意 CLI
    args: ["run"]
    env: {}
  watchdog:
    maxRetries: 2              # 失败后额外重试几次
    backoffSec: 60             # 重试前等多久
    idleTimeoutSec: 1800       # 多久没输出判定卡死
    totalTimeoutSec: 7200      # 单任务最长跑多久
    killGraceSec: 15           # 终止后等多久再强杀
  decision:
    mode: attended             # attended | unattended
    timeoutSec: 600            # 决策窗口等多久
    resume: session            # session | restart
    outputFormat: json         # json（能拿 sessionID）| text
    sessionArgs: ["--session", "{session}"]
  state:
    dir: .overnight-runner
  workdir: .
  ui:
    refreshHz: 8
    logTail: 400
```

### 2. 队列定义 `.overnight-runner/queue/<name>/queue.yaml`

管 **跑什么**。plan 用 **相对项目根** 的路径。

```yaml
queue:
  - id: 20261103-feature-a
    plan: docs/plans/20261103-feature-a.md
    prompt: "按 plan 实现，完成后跑一遍自测"
    role: DEV
    priority: 10
    depends_on: []
```

队列可以直接改 YAML，也可以用 `add` 追加（会写回 YAML，**保留其它任务不动**）。

### 3. 项目配置 `.overnight-runner/project.yaml`

管 **怎么决策**。

```yaml
project:
  name: my-project
  agent:
    command: opencode
    args: ["run"]

default:
  prompt: |
    你在无人值守模式下工作，不要停下来等待人工确认。
    {{DECISIONS}}
    {{PLAN}}
    每做出一个决策，输出一行：DECISION: <问题> → <决策>
    全部完成后输出一行：DONE: <总结>
  onUnknownDecision: 跳过并记录到决策日志

decisions:
  - id: db-migration
    question: 是否执行数据库迁移脚本？
    match: "数据库迁移|migration"
    answer: 先写好回滚脚本，再执行迁移
    enabled: true
```

占位符：`{{PLAN}}` = plan 全文，`{{DECISIONS}}` = 决策清单。

`match` 是正则，`question` 是精确 / 包含匹配。`enabled: false` 可以临时停用某条规则。

## 决策记录

每次用到决策都追加一条到 `.overnight-runner/queue/<name>/decisions.jsonl`：

```json
{"at": "2026-11-03T02:14:22+08:00", "task_id": "20261103-feature-a",
 "question": "是否执行数据库迁移脚本？", "answer": "先写好回滚脚本，再执行迁移",
 "source": "rule", "rule_id": "db-migration", "waited_sec": 0, "session_id": ""}
```

| source | 含义 |
|---|---|
| `rule` | 命中预设规则（无人值守，或有人值守但超时兜底） |
| `fallback` | 没命中任何规则，用了 `onUnknownDecision` 兜底 |
| `agent` | agent 自己按默认决策做完了，输出了 `DECISION:` |
| `human` | **人在决策窗口里回答的** |
| `timeout` | **决策窗口等超时，自动兜底的** |

**回溯时先看这个文件**，就知道"昨晚它替我做了什么决定"。

## agent 契约

agent 通过 stdout 跟 runner 通信：

| 输出 | 含义 |
|---|---|
| `DECISION: <问题> → <决策>` | 做了一个决策（会被记录） |
| `QUESTION: <问题>` | 抛出待决问题（`attended` 打断问人 / `unattended` 按规则回答） |
| `DONE: <总结>` | 任务完成 |
| `BLOCKED: <原因>` | 任务阻塞 |
| 其它行 | 普通日志，原样显示在右侧 |

`outputFormat: json` 时，agent 输出按 **json 事件** 解析（每行一个事件），
runner 从事件里取 `sessionID` —— 这是"把决策送回给 agent"的前提。
换不支持 json 输出的 agent 时把 `outputFormat` 改成 `text`（此时靠 `sessionPattern` 正则抓 session id）。

## 看门狗

| 情况 | 判定 | 动作 |
|---|---|---|
| agent 退出码 ≠ 0 | 失败 | 退避后重试，超过次数标记失败 |
| 空闲超过 `idleTimeoutSec` | 卡死 | 终止进程组，退避后重试 |
| 超过 `totalTimeoutSec` | 超时 | 终止进程组，退避后重试 |

终止时先 `SIGTERM`（Windows 是 `CTRL_BREAK`），宽限期后 `SIGKILL`，
**整组进程一起杀**（POSIX 用 `killpg`，Windows 用进程组），不留孤儿进程。

重试时会把之前做过的决策一起带上，避免 agent 重复问同一个问题。

## 架构

```
┌──────────────────────────────────────────────┐
│ ui.py（自绘 ANSI 分屏）                        │
│  左：任务队列   右：agent 输出 + 决策窗口      │
│  term.py：备用屏幕 / 光标 / 边框 / 语义色       │
└───────────────┬──────────────────────────────┘
                │
┌───────────────▼──────────────────────────────┐
│ controller.py                                 │
│  取任务 → 组 prompt → 跑 agent → 看门狗        │
│  → agent 提问？→ 打断 → 等人决策 → session 续跑 │
└──┬────────────┬───────────────┬──────────────┘
   │            │               │
   ▼            ▼               ▼
queue.py    prompts.py      agent.py
(队列目录)   (默认提示词)     (子进程+json解析)
                │               │
                ▼               ▼
         decisions.py       watchdog 判定
         (规则+记录+回灌)

config.py ──→ yaml_lite.py（零依赖 YAML 子集）
util.py ──→ QueueLock（单实例锁）
```

## 注意

- **只跑已经确认过的 plan。** runner 不做人工确认这一关 —— plan 质量是人的责任。
- 队列定义与项目配置 **提交进仓库**；`state.json` 与 `logs/` 不要提交。
- 同一条队列 **不能同时跑两个 runner**（`.lock` 挡住，第二个退出码 2）。
- agent 命令要支持"非交互跑一次"的用法（`opencode run "<prompt>"` 这种）。
- 面板需要真终端；`--headless` 可以在管道 / CI 里用（headless 强制无人值守模式）。

## 相关

- [`../agile-team-sdd/`](../agile-team-sdd/) — 产出 plan 的 skill（`dev-plan`），runner 消费的就是 plan
- [`../team-workflow-guide/`](../team-workflow-guide/) — 流程与角色约定
