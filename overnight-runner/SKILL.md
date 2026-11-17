---
name: overnight-runner
description: 启动 overnight-runner 分屏面板，把队列里的 plan 交给 coding agent 跑（左边任务队列，右边 agent 输出，支持多队列、看门狗重试、有人值守时的决策窗口与无人值守时的默认决策记录）。当用户说"跑一晚上"、"夜间跑这些 plan"、"启动 overnight runner"、"无人值守跑任务"、"跑一条新队列"、"多个队列分别跑"时使用。
---

# overnight-runner

把一串 **plan** 交给 coding agent 无人值守地跑：左边是任务队列，右边是 agent 的实时输出。

## 它解决什么

一次要跑好几个 plan，人守着点 `opencode run` 没人愿意干。
这个工具把这件事变成 **配置 + 启动**：

- 队列用 YAML 管，plan 用相对路径引用；**一条队列一个目录**，多人各跑各的
- 跑起来是分屏面板：左边看队列状态，右边看 agent 在干什么
- agent 卡死或失败，看门狗自动重试
- 决策按预设规则自动做，**每一条都记下来**，事后可回溯
- 白天有人值守时，agent 提问会弹 **带倒计时的决策窗口**；超时没人答就自动兜底

## 安装

```bash
# 装到当前项目
./overnight-runner/scripts/install.sh .

# 预览
./overnight-runner/scripts/install.sh . --dry-run

```

**零依赖**：只用 Python 3.9+ 标准库，不用 pip install。

装完项目里会有：

```
<项目>/
├── overnight-runner.yaml              # 运行配置（提交进仓库，全队列共享）
├── .overnight-runner/
│   ├── project.yaml                   # 项目配置：默认提示词 + 默认决策（提交）
│   └── queue/
│       └── default/                   # 一条队列一个目录
│           ├── queue.yaml             # 队列定义：跑哪些 plan（提交）
│           ├── state.json             # 运行时状态（不提交）
│           ├── decisions.jsonl        # 决策记录（提交，便于回溯）
│           ├── logs/                   # 每个任务的 agent 日志（不提交）
│           └── .lock                   # 单实例锁（不提交）
└── tools/overnight-runner/
    ├── overnight-runner               # 启动脚本（POSIX）
    ├── overnight-runner.cmd           # 启动脚本（Windows）
    └── overnight_runner/              # 实现
```

**老项目自动迁移**：老布局（队列写在项目根 `overnight-runner.yaml`）第一次运行时会
自动搬到 `.overnight-runner/queue/default/`，不丢任务、不丢状态，迁移幂等。

**依赖**：**没有**。只用 Python 3.9+ 标准库 —— 界面是自绘的 ANSI 转义序列，
配置解析是自己实现的 YAML 子集。Windows / macOS / Linux 都支持。

## 用法

```bash
OR=tools/overnight-runner/overnight-runner

$OR init                                   # 初始化配置
$OR add docs/plans/20261103-feature-a.md  # 追加 plan（相对项目根）
$OR add docs/plans/xxx.md --role QA --priority 20
$OR list                                   # 看队列
$OR status                                 # 看状态
$OR queues                                 # 看所有队列
$OR run                                    # 启动分屏面板
$OR run --headless                         # 无界面（CI / 脚本）
$OR run --headless --retry-failed          # 把上次失败的重新排一遍
$OR run --mode unattended                   # 临时切成无人值守
$OR decisions                              # 看决策记录
```

### 多队列（多人各跑各的）

所有子命令都支持全局参数 `--queue <名字>`（默认 `default`）：

```bash
$OR --queue alice add docs/plans/alice-feature.md
$OR --queue bob   add docs/plans/bob-feature.md
$OR queues            # 一屏看清有几条队列、各自什么状态
$OR --queue alice run # 跑 alice 队列
```

每条队列的状态、日志、决策记录完全隔离；**默认决策规则是项目级共享**的
（都在 `.overnight-runner/project.yaml`）—— 规则是"项目怎么做决定"，决策 **记录** 才是
"这条队列发生过什么"。

同一条队列 **不能同时跑两个 runner**（`.lock` 挡住，第二个退出码 2）。

### 决策模式：白天有人值守 / 夜里无人值守

| | `attended`（有人值守） | `unattended`（无人值守） |
|---|---|---|
| agent 提问时 | **打断 agent**，TUI 弹决策窗口 | 不打断，agent 继续跑 |
| 谁来决策 | 人（600 秒内）→ 超时自动兜底 | 规则 → `onUnknownDecision` 兜底 |
| 决策记录 source | `human` / `timeout` | `rule` / `fallback` |

配置在 `overnight-runner.yaml` 的 `runner.decision.mode`；
命令行 `run --mode attended|unattended` 可临时覆盖。**`--headless` 强制无人值守。**

决策窗口出现时按键被决策框独占：`Enter` 提交答案（agent 用 `--session` 续跑，上下文不丢）·
`Esc` 立刻用默认决策 · `Ctrl-C` 退出。

### 面板操作

| 键 | 作用 |
|---|---|
| `↑` `↓` | 选择任务 |
| `a` | 追加 plan（就地输入路径） |
| `r` | 重置选中任务为待跑 |
| `p` | 暂停 / 恢复 |
| `d` | 移除 |
| `Enter` | 看选中任务的完整日志 |
| `Esc` | 返回实时输出 |
| `c` | 清屏 |
| `q` | 退出 |

## 队列定义（`.overnight-runner/queue/<名字>/queue.yaml`）

```yaml
queue:
  - id: 20261103-feature-a
    plan: docs/plans/20261103-feature-a.md   # 相对项目根
    role: DEV
    priority: 10
```

**plan 用相对项目根的路径。** 队列定义在 YAML 里，可以直接改，也可以用 `add` 追加（会写回 YAML）。

## 运行配置（`overnight-runner.yaml`）

```yaml
runner:
  agent:
    command: opencode          # 或 claude / codex / 任意 CLI
    args: ["run"]
  watchdog:
    maxRetries: 2              # 失败后额外重试几次
    backoffSec: 60             # 重试前等多久
    idleTimeoutSec: 1800       # 多久没输出判定卡死
    totalTimeoutSec: 7200      # 单任务最长跑多久
  decision:
    mode: attended             # attended（有人值守）| unattended（无人值守）
    timeoutSec: 600            # 决策窗口等多久（秒）
    resume: session            # session（续跑）| restart（重跑任务）
    outputFormat: json         # json（能拿 sessionID）| text
```

## 项目配置（`.overnight-runner/project.yaml`）

回答"无人值守时怎么决策"：

```yaml
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
```

`{{PLAN}}` = plan 全文，`{{DECISIONS}}` = 下面的决策清单。

## 决策记录

每次用到决策，都会追加一条到 `.overnight-runner/queue/<名字>/decisions.jsonl`：

```json
{"at": "2026-11-03T02:14:22+08:00", "task_id": "20261103-feature-a",
 "question": "是否执行数据库迁移脚本？", "answer": "先写好回滚脚本，再执行迁移",
 "source": "rule", "rule_id": "db-migration", "waited_sec": 0, "session_id": ""}
```

`source` 五种：

| source | 含义 |
|---|---|
| `rule` | 命中预设规则 |
| `fallback` | 没命中任何规则，用了兜底策略 |
| `agent` | agent 自己按默认决策做完了，并输出了 `DECISION:` |
| `human` | 人在决策窗口里回答的 |
| `timeout` | 决策窗口等超时，自动兜底的 |

**回溯时先看这个文件**，就知道"昨晚它替我做了什么决定"。

## agent 契约

agent 通过 stdout 跟 runner 通信：

| 输出 | 含义 |
|---|---|
| `DECISION: <问题> → <决策>` | 做了一个决策（会被记录） |
| `QUESTION: <问题>` | 抛出待决问题（runner 用规则回答并记录） |
| `DONE: <总结>` | 任务完成 |
| `BLOCKED: <原因>` | 任务阻塞 |
| 其他行 | 普通日志，原样显示在右侧 |

## 看门狗

| 情况 | 判定 | 动作 |
|---|---|---|
| agent 退出码 ≠ 0 | 失败 | 退避后重试，超过次数标记失败 |
| 空闲超过 `idleTimeoutSec` | 卡死 | 终止进程组，退避后重试 |
| 超过 `totalTimeoutSec` | 超时 | 终止进程组，退避后重试 |

终止时会先 `SIGTERM`（Windows 是 `CTRL_BREAK`），宽限期后 `SIGKILL`，
**整组进程一起杀**，不会留孤儿进程。

重试时会把之前做过的决策一起带上，避免 agent 重复问同一个问题。

## 注意

- **只跑已经确认过的 plan。** runner 不做人工确认这一关 —— plan 质量是人的责任。
- 队列定义与项目配置 **提交进仓库**；`state.json` 与 `logs/` 不要提交。
- 同一条队列 **不能同时跑两个 runner**（`.lock` 挡住，第二个退出码 2）。
- agent 命令要支持"非交互跑一次"的用法（`opencode run "<prompt>"` 这种）。
- 面板需要真终端；`--headless` 可以在管道 / CI 里用（headless 强制无人值守模式）。
