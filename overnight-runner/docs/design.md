# overnight-runner 设计

## 目标

把"一串 plan 交给 coding agent 无人值守地跑"变成一个 **可配置、可观测、可回溯** 的工具。

四条硬需求：

1. 作为一个 skill 启动，任何人都能装进自己的项目
2. 分屏：左边任务管理，右边 coding agent
3. 启动用 YAML 管队列，plan 用相对路径引用
4. 支持追加 plan
5. 失败有看门狗重试
6. 支持 win / mac
7. 项目配置：默认提示词 + 默认决策，决策要写记录

## 模块

```
overnight_runner/
├── cli.py          命令行入口（init/add/list/status/decisions/queues/run）
├── config.py       三层 YAML 配置的加载与序列化 + 队列路径解析 + 老布局迁移
├── yaml_lite.py    零依赖 YAML 子集解析/序列化
├── queue.py        任务模型、队列、状态持久化（按队列目录隔离）
├── prompts.py      提示词组装（默认提示词 + 决策清单 + plan 全文 + 续跑提示）
├── decisions.py    默认决策规则匹配 + 决策记录
├── agent.py        子进程启动、流式输出、json 事件解析、session id 抓取
├── controller.py   调度：取任务 → 跑 → 看门狗 → 决策打断 → 续跑 → 重试 → 落状态
├── keys.py         跨平台按键读取（termios / msvcrt）
├── ui.py           分屏界面 + 决策窗口
├── term.py         ANSI 绘制原语（备用屏幕 / 光标 / 边框 / 宽度计算）
└── util.py         时间、原子写、JSONL 追加、队列单实例锁
```

**零第三方依赖**：只用 Python 3.9+ 标准库。

## 配置分层

| 文件 | 管什么 | 作用域 | 提交进仓库 |
|---|---|---|---|
| `.overnight-runner/overnight-runner.yaml` | agent 命令 + 看门狗 + UI + 决策策略 | 项目 | ✅ |
| `.overnight-runner/project.yaml` | 默认提示词 + 默认决策规则 | 项目（全队列共享） | ✅ |
| `.overnight-runner/queue/<n>/queue.yaml` | 队列定义（跑哪些 plan） | 单条队列 | ✅ |
| `.overnight-runner/queue/<n>/state.json` | 运行时状态（谁跑过、重试几次） | 单条队列 | ❌ |
| `.overnight-runner/queue/<n>/decisions.jsonl` | 决策记录 | 单条队列 | ✅（便于回溯） |
| `.overnight-runner/queue/<n>/logs/*.log` | 每个任务的 agent 原始输出 | 单条队列 | ❌ |
| `.overnight-runner/queue/<n>/.lock` | 单实例锁（pid + 心跳） | 单条队列 | ❌ |

**三层分离的理由**：

- **runner 级**（怎么跑）：agent 是谁、看门狗多严、决策怎么处理 —— 项目级策略，
  跟"跑哪些任务"无关。
- **project 级**（怎么决策）：默认决策规则是"这个项目永远怎么做决定"，
  很少变，应该沉淀下来复用，**所有队列共享一份**。
- **queue 级**（跑什么）：队列经常变（按迭代切分支、按人分工），
  多人各跑各的互不干扰，所以 **一条队列一个目录**。

**为什么决策记录分队列、决策规则不分**：规则是项目级策略（"i 不在的时候你该怎么做"），
记录是 per-queue 的事实（"alice 这条队列昨晚发生过什么"）。混在一起会互相污染。

## 多队列

```
<project>/
├── overnight-runner.yaml
└── .overnight-runner/
    ├── project.yaml
    └── queue/
        ├── default/{queue.yaml, state.json, logs/, decisions.jsonl, .lock}
        └── alice/{queue.yaml, state.json, logs/, decisions.jsonl, .lock}
```

- 队列名白名单 `[A-Za-z0-9][A-Za-z0-9._-]*` —— **拒绝 `..`**，防路径穿越。
- 所有子命令都支持全局 `--queue <name>`（默认 `default`）。
- `queues` 子命令一屏看清有几条队列、各自什么状态。

### 老布局迁移（幂等）

老布局：队列写在 overnight-runner.yaml 的 `queue:` 段（根目录或 `.overnight-runner/`），
状态在 `.overnight-runner/state.json`，日志在 `.overnight-runner/logs/`。

任何读队列的子命令都会触发迁移：

| 源 | 目标 |
|---|---|
| `.overnight-runner/overnight-runner.yaml`（或旧根文件）的 `queue:` 段 | `.overnight-runner/queue/default/queue.yaml` |
| `<root>/.overnight-runner/state.json` | `.overnight-runner/queue/default/state.json` |
| `<root>/.overnight-runner/logs/` | `.overnight-runner/queue/default/logs/` |
| `<root>/.overnight-runner/decisions.jsonl` | `.overnight-runner/queue/default/decisions.jsonl` |

**用 move（rename）不是 copy** —— 源文件不会留下两份。迁移后把根配置里的 `queue:` 段清空，
保证"只发生一次"。源文件不存在就跳过，重复调用无副作用。

### 单实例锁

同一个队列目录同时跑两个 runner → 两边都认领同一个 pending 任务 → **同一个 plan 跑两遍**
（白烧 agent）。所以每条队列目录放一个 `.lock`（`{"pid", "started_at", "heartbeat"}`）：

- 锁不存在 → 创建
- 锁存在且 pid **活着** → 报错退出（退出码 `2`），提示"队列 X 已被 pid N 占用"
- 锁存在但 pid 已死（stale）→ 视为残留，清理后重建
- 正常退出 / Ctrl-C → 删除自己持有的锁

pid 存活探测用 `os.kill(pid, 0)`（POSIX）。Windows 上 `os.kill(pid, 0)` 会真的杀进程，
所以 Windows 走心跳判断（超过 `STALE_SEC` 视为 stale）。

## 状态机

任务状态：

```
pending ──▶ running ──┬──▶ success
   ▲          │        ├──▶ retrying ──▶ running   (退避后重试)
   │          │        ├──▶ failed
   │          │        └──▶ blocked
   └──────────┴── (r 键重置)
```

`next_ready()` 选下一个任务的条件：`enabled` 且 `status == pending` 且所有 `depends_on` 已 `success`，
按 `priority` 升序，同优先级按 id。

## 决策机制

五种来源，都写进 `decisions.jsonl`：

| source | 触发方式 | 记录内容 |
|---|---|---|
| `agent` | agent 输出 `DECISION: <问题> → <决策>` | agent 自己做的决定 |
| `rule` | agent 输出 `QUESTION:`，命中预设规则 | 问题 + 规则答案 + rule_id |
| `fallback` | agent 输出 `QUESTION:` 但没命中规则 | 问题 + `onUnknownDecision` 兜底 |
| `human` | **人在 TUI 决策窗口里回答的** | 问题 + 人的答案 + 等了多久 + session id |
| `timeout` | **决策窗口等超时，自动兜底的** | 问题 + 兜底答案 + 等了多久 + session id |

### 两种决策模式

| | `attended`（白天有人值守） | `unattended`（夜里无人值守） |
|---|---|---|
| agent 提问时 | **打断 agent**，TUI 弹决策窗口 | 不打断，agent 继续跑 |
| 谁来决策 | 人（`timeoutSec` 内）→ 超时自动兜底 | 规则 → `onUnknownDecision` 兜底 |
| 记录 source | `human` / `timeout` | `rule` / `fallback` |

**为什么按"有没有人盯着"分，而不是按"问题命不命中规则"分**：
规则表在 attended 模式里只当 **超时兜底** 用 —— 它的语义是"我不在的时候你该怎么做"。
白天有人就问人，问不到再用规则兜底。

`--headless` **强制** `unattended` —— 没人看面板，卡在等 600 秒纯属浪费。

### 决策状态机

```
agent 输出 QUESTION: <问题>
        │
        ▼
  ┌──────────────────────────┐
  │ mode = ?                │
  │ unattended          → 否 │──► 自动决策（规则答案 or onUnknownDecision）
  │ attended            → 是 │         └─► 记录 source=rule / fallback
  └──────────────────────────┘         └─► 继续跑（决策在下次拉起时注入 prompt）
        │ 是
        ▼
  终止 agent（TERM → 宽限 → KILL）
        │
        ▼
  置 PendingQuestion{deadline = now + timeoutSec}
        │
        ▼
  ┌──────────── 等待（TUI 弹决策窗口，倒计时）─────────────┐
  │ 人按 Enter 提交答案 ──────────► source=human          │
  │ 人按 Esc 立刻兜底 ────────────► source=timeout        │
  │ 倒计时到点没人管 ─────────────► source=timeout        │
  └───────────────────────────────────────────────────────┘
        │ 超时兜底时：规则命中 → 规则答案；未命中 → onUnknownDecision
        ▼
  记录到 decisions.jsonl
        │
        ▼
  ┌──────────── 恢复 ────────────┐
  │ resume=session 且拿到 sid    │──► agent --session <sid> "<答案>，请继续>"
  │ 否则 / 续跑失败              │──► 重跑任务，prompt 里带决策历史
  └─────────────────────────────┘
```

**三条出路保证不会卡死**：人答（`Enter`）、人放弃（`Esc`）、超时自动兜底。
Ctrl-C 退出整个 runner。

### 打断 agent 续跑：session 通道

`opencode run` **没有**"运行中接收输入"的选项，只有 `--session` / `--continue` 两种续跑方式
（已实测）。所以"人回答问题"的实现路径只能是：

```
终止 agent → 拿到答案 → opencode run --session <sid> "<答案>，请继续>"
```

前提是能拿到 `sessionID`：

- `outputFormat: json` 时，每条 json 事件顶层都带 `sessionID` —— **这是主路径**
- `outputFormat: text` 时，用 `sessionPattern` 正则从原始行里兜底抓

拿不到 session id → 降级为 **重跑整个任务**，决策历史注入新一轮 prompt。
续跑进程立刻非零退出 → 再降级一次（避免无限重试）。

### 决策历史注入

每次决策后 `decisions_made` **必须 append**，且每次拉起 agent 前都拼进 prompt
（不只是重试时）：

```
已经做出的决策（不要重复询问）：
- 扩范围改还是先修 Bug？ → 先修 Bug，不要扩大改动范围
```

这样即使 `unattended`（完全不打断），agent 也能在下一轮看到之前的决策 ——
修掉了"决策是假的"（答案从不回灌给 agent）这个既有缺陷。

## 看门狗

两个超时，都以 **agent 最后一次输出** 为基准：

- `idleTimeoutSec`：空闲超时 —— agent 卡死 / 死锁 / 在等输入
- `totalTimeoutSec`：总时长超时 —— agent 在做无用功

判定在 controller 的轮询循环里做（0.5s 一次），超时后：

1. `SIGTERM`（Windows `CTRL_BREAK_EVENT`）
2. 等 `killGraceSec`
3. 还没死就 `SIGKILL`

**进程组终止**：POSIX 用 `start_new_session=True` + `os.killpg`，
Windows 用 `CREATE_NEW_PROCESS_GROUP` + `CTRL_BREAK_EVENT`。
只杀父进程会留下孙子进程（agent 通常会再起子进程）。

重试次数 `maxRetries`，退避 `backoffSec`。

## 跨平台

| 关注点 | macOS / Linux | Windows |
|---|---|---|
| 按键读取 | `termios` + `tty.setraw` | `msvcrt.getwch()` |
| 进程组 | `start_new_session` + `killpg` | `CREATE_NEW_PROCESS_GROUP` + `CTRL_BREAK` |
| 强杀 | `SIGKILL` | `proc.kill()` |
| 启动脚本 | `overnight-runner`（bash） | `overnight-runner.cmd` |
| 换行 | `\n` | `\r\n`（Python 文本模式自动处理） |

全部用标准库实现，不需要 `pip install`：
按键（`termios` / `msvcrt`）、进程组（`os.killpg` / `CREATE_NEW_PROCESS_GROUP`）、
界面（ANSI 转义序列）、YAML 解析（`yaml_lite.py`）。

## 界面

自己用 ANSI 转义序列画（`term.py`），不用 rich：

| 能力 | 实现 |
|---|---|
| 全屏 | `ESC[?1049h` 进备用屏幕，退出时 `ESC[?1049l` 恢复 |
| 光标 | `ESC[{row};{col}H` 绝对定位 + `ESC[?25l` 隐藏 |
| 边框 | `┌┐└┘─│` 圆角字符，逐格定位 |
| 颜色 | SGR 序列，状态用固定语义色 |
| 宽度 | 按 `east_asian_width` 算，中文算 2 列；**忽略 ANSI 序列本身占位** |

布局：

```
┌ 任务队列 (N) ────────┐┌ Coding Agent · <task-id> ──────────────────────────┐
│▶ 20261103-feature-a 运行中│ $ opencode run "…"                                  │
│  20261103-bugfix    成功 │ DECISION: 是否执行数据库迁移？ → 先写回滚脚本         │
│                        │ …                                                      │
│ 待跑 1 · 运行 1 · 成功 1│ 最近决策                                                │
└────────────────────────┘└─────────────────────────────────────────────────────┘
↑↓ 选择  a 追加 plan  r 重试  p 暂停/恢复  d 移除  Enter 查看日志  Esc 返回  q 退出
```

**宽度计算必须忽略 ANSI 序列**：带颜色的文本如果按字符数算宽，
边框就会错位。所以 `dwidth()` / `truncate()` / `pad()` / `wrap()` 都走同一个
`_tokens()`，把转义序列当宽度 0。

按键在独立线程读（`KeyReader`），避免阻塞渲染循环。
追加 plan 用 **行内输入模式**（不是弹窗）：按 `a` 进入输入态，
后续按键进缓冲区，`Enter` 确认，`Esc` 取消。

**决策窗口**（`attended` 模式，agent 提问时抢占右栏）：

```
◆ 待决策
  任务: 20261106-fix-public-endpoints

  扩范围改还是先修 Bug？

  你的决策：
  > 先修 Bug，不要扩大改动范围▏

  剩余 9:58   Enter 确认 · Esc 用默认决策 · Ctrl-C 退出
```

- **按键路由优先级**：决策窗口 > 追加 plan 输入 > 常规。决策窗口在阻塞 agent，等不起。
- 右栏标题用 **正在跑** 的任务（`_running_task()`）而不是 **选中行** ——
  否则按 `↓` 切行后标题和内容对不上。

### 按键读取必须懂 UTF-8

`keys.py` 不能"一次 `os.read(fd, 1)` 再解码" —— 汉字是 3 字节、emoji 是 4 字节，
一次读一个字节会把一个字符拆成 3 次读，每次 `decode(errors="replace")` 都失败，
**中文全变问号**（实测：决策窗口输入"先修 Bug"，落盘变成"??? Bug"）。

做法（`PosixKeyReader`）：

| 步骤 | 说明 |
|---|---|
| 缓冲 | 字节先进缓冲区，不假设一次 read 就是一个键 |
| 凑齐 | 按 UTF-8 首字节判断字符长度（1/2/3/4），字节够了才解 |
| ESC 判定 | ESC 后等 50ms；是 `ESC [` 就按 CSI 规则在 **缓冲区里** 找结束字节，不是再读 2 字节 |

Windows 走 `msvcrt.getwch()`，它本身就返回完整字符，不受这个问题影响。

## 已知取舍

| 取舍 | 原因 |
|---|---|
| agent 非交互调用（`opencode run "<prompt>"`） | runner 无法接管交互式 TUI 的终端输入；提示词走命令行参数 |
| 提示词不进 `--prompt-file` | 不同 agent 参数格式不一致；用命令行参数兼容性最好。超长提示词在 Windows 上有长度限制，这是已知限制 |
| 自己实现 YAML 子集 | 为了零依赖。覆盖了本项目用到的全部语法，遇到不支持的语法（锚点/别名/标签）会明确报错而不是静默出错 |
| 自己实现 ANSI 绘制 | 为了零依赖。代价是没有 rich 的自动换行与布局引擎，长文本要自己算宽 |
| 决策记录用 JSONL | 追加写、原子、无需数据库、方便 `jq` 处理 |
| 状态单独放 `state.json` | 队列 YAML 要提交，状态不要；分开才能既版本化又不脏仓库 |
| 状态文件旁存 `state.json.bak` | 误删状态文件不该把已跑完的任务全部重新排队；读取时主文件缺失/损坏就回落 `.bak` |
| 一条队列一个目录 | 多人可以在同一个仓库里各跑各的，状态与日志互不串；代价是路径多一层 |
| 老布局自动迁移而不是报错 | 用户不该为了升级改配置；迁移用 move 且幂等，只发生一次 |
| 面板不解析 agent 的 ANSI | agent 的原始输出原样透传，保留它的配色；代价是右侧可能有转义序列残留 |
| 打断 agent 而不是挂起等待 | agent 没有"挂起等输入"的接口（`opencode run` 只有 `--session` 续跑）；打断后用 session 续跑保住上下文 |
| 按键读取用字节缓冲而不是一次读一个键 | 一次读一个字节会把汉字拆成乱码；缓冲 + 按 UTF-8 首字节凑齐才能正确还原中文 |
