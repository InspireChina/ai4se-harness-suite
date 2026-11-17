---
name: overnight-runner-template
description: 启动 overnight-runner 分屏面板，把队列里的 plan 交给 coding agent 跑（多队列、看门狗重试、有人值守决策窗口 / 无人值守默认决策）。当用户说"跑一晚上"、"夜间跑这些 plan"、"启动 overnight runner"、"无人值守跑任务"、"跑一条新队列"时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# overnight-runner

把一串 **已确认的 plan** 交给 coding agent 无人值守地跑：左边任务队列，右边 agent 实时输出。

**硬性**：只跑已人工确认的 plan；本 skill **不做** Plan / HLD 闸门本身。

## 前置

1. 项目里已有 `{{OVERNIGHT_DIR}}/`（含启动脚本与配置）。没有则先安装：

```bash
{{HARNESS_ROOT}}/overnight-runner/scripts/install.sh {{PROJECT_ROOT}}
```

2. Plan 路径相对项目根，通常在 `{{FEATURES_DIR}}/<迭代>/<CODE>-<slug>/plan.md` 或 `{{CHORES_DIR}}/plan-{slug}.md`。

## 常用命令

```bash
OR={{OVERNIGHT_DIR}}/overnight-runner

$OR init
$OR add {{FEATURES_DIR}}/<迭代>/<CODE>-<slug>/plan.md
$OR add {{FEATURES_DIR}}/<迭代>/<CODE>-<slug>/plan.md --role DEV --priority 10
$OR list
$OR status
$OR queues
$OR run                          # 分屏面板
$OR run --headless               # 无 TTY / CI（强制 unattended）
$OR run --mode unattended        # 临时无人值守
$OR run --headless --retry-failed
$OR decisions
```

多队列（`--queue <名>`，默认 `default`）：

```bash
$OR --queue alice add {{FEATURES_DIR}}/<迭代>/<CODE>-<slug>/plan.md
$OR --queue alice run
```

同一队列不能并行两个 runner（`.lock`，冲突时退出码 2）。

## 决策模式

| | `attended` | `unattended` |
|---|---|---|
| agent 提问 | 打断，TUI 决策窗口 | 不打断，规则/兜底 |
| 记录 source | `human` / `timeout` | `rule` / `fallback` |

配置：`{{OVERNIGHT_DIR}}/overnight-runner.yaml` → `runner.decision.mode`。  
`--headless` **强制** unattended。

## 面板按键

| 键 | 作用 |
|---|---|
| `↑` `↓` | 选任务 |
| `a` | 追加 plan |
| `r` | 重置为待跑 |
| `p` | 暂停 / 恢复 |
| `d` | 移除 |
| `Enter` | 看完整日志 |
| `Esc` | 回实时输出 |
| `q` | 退出 |

决策窗口：`Enter` 提交 · `Esc` 兜底 · `Ctrl-C` 退出。

## 配置要点

- 队列：`{{OVERNIGHT_DIR}}/queue/<名>/queue.yaml`（`plan` 用相对项目根路径）
- 运行：`{{OVERNIGHT_DIR}}/overnight-runner.yaml`（agent 命令、看门狗、决策超时）
- 项目决策：`{{OVERNIGHT_DIR}}/project.yaml`（`decisions` 规则 + `onUnknownDecision`）
- 决策记录：`{{OVERNIGHT_DIR}}/queue/<名>/decisions.jsonl`（回溯用）

提交：`queue.yaml` / `project.yaml` / `overnight-runner.yaml` / `decisions.jsonl`。  
不提交：`state.json`、`logs/`、`.lock`。

## agent 契约（stdout）

| 输出 | 含义 |
|---|---|
| `DECISION: <问题> → <决策>` | 记录决策 |
| `QUESTION: <问题>` | 待决（规则或人答） |
| `DONE: <总结>` | 完成 |
| `BLOCKED: <原因>` | 阻塞 |

## 怎么做（本 skill）

1. 确认目标 plan 已人工确认，路径相对 `{{PROJECT_ROOT}}`
2. 若缺 `{{OVERNIGHT_DIR}}/`，先跑安装命令
3. `add` 进合适队列（或改 `queue.yaml`）
4. 按场景选 `run` / `run --mode unattended` / `run --headless`
5. 结束后用 `decisions` / `decisions.jsonl` 回溯替你做的决定

## 自检

- [ ] 只加入了已确认的 plan
- [ ] 队列 / 模式选择正确（白天 attended，夜里或 CI 用 unattended / headless）
- [ ] 需要的决策规则已在 `project.yaml`
- [ ] 运行后看过决策记录或失败任务状态
