# 引擎记录每个子 agent 调用的耗时

## 目标

`decisions.jsonl` 里每条「调用子 agent」的记录带 **耗时**，供机器统计：哪个节点最费时间、一批任务里哪条最慢、失败的那次花了多久。

不做实例目录、不做 status、不做续跑。

## 现状

- `Runner._call()` 是唯一的调用点（`runner.py#L204-L206`），但只返回 stdout 字符串，没有计时
- 三个业务调用点：gate（`run()` L164）、action（`_run_action()` L195）、batch-step（L188）
- 日志跑完才落盘（`cli.py#L106-L113`），异常时整份丢

## 改动

### 1. `runner.py`：`_call` 变成「结果 + 计时」

```python
def _call(self, node, task):
    model = _resolve_model(self.graph, node, self.master_model)
    started_at = datetime.now().astimezone().isoformat(timespec="milliseconds")
    t0 = time.perf_counter()
    try:
        text = self.agent(node, model, task)
    except BaseException:
        timing = {"startedAt": started_at, "durationMs": _ms(t0)}
        self._record_failure(node["id"], timing)   # 失败也留一笔
        raise
    return text, {"startedAt": started_at, "durationMs": _ms(t0)}
```

- 耗时用 `time.perf_counter()`（单调时钟，不受系统时间调整影响）
- `startedAt` 用带时区 ISO（`datetime.now().astimezone()`），纯标准库，3.9 可用
- `_ms(t0)` = `int(round((time.perf_counter() - t0) * 1000))`

### 2. 三个调用点把 timing 摊进记录

```python
result, timing = self._call(node, None)
self.log.append(dict({"node": node_id, "event": "action", "output": result, "model": ...}, **timing))
```

落到的记录：

| event | 带耗时 | 说明 |
|---|---|---|
| `gate` | ✅ | 门禁 agent 判「满意/不满意」的时间 |
| `action` | ✅ | 常规节点 |
| `batch-step` | ✅ | **逐条**任务各自的耗时 |
| `error`（新增） | ✅ | 子 agent 失败/超时，先记一笔再抛，机器能看出「卡在哪个节点、烧了多久」 |
| 其余事件 | — | `decision` / `human_input` / `milestone` / `end` / `fork` / `join-wait` / `model-check` 不调 agent，不加字段 |

### 3. 记录形状

```json
{"node":"dev-build","event":"action","startedAt":"2026-11-19T17:29:41.003+08:00","durationMs":144409,"output":"...","model":"writer"}
```

只加两个字段，不改任何已有字段名，老记录照旧能读。

## 测试（`tests/test_units.py`）

现有 25 个用例用 `assertIn` 断言子串，**不会因为多两个字段而挂**。新增 3 个：

1. `test_action_records_duration`：`action` 与 `gate` 记录都有 `durationMs`（≥0 的整数）和可被 `datetime.fromisoformat` 解析的 `startedAt`
2. `test_batch_step_each_has_duration`：一节点出两条任务 → 两条 `batch-step` 各带自己的数字
3. `test_failed_call_records_duration`：假 agent 抛非零退出 → 抛 `GraphError` 前日志里有一条 `event=error` 且带 `durationMs`

## 文档

- `agents-workflow-engine/README.md`：「图的语义」表旁补一小段「记录字段」，说明 `startedAt` / `durationMs` 的含义与哪些事件带它
- 不动根 README / AGENTS.md / `graph.html` / 预设 YAML

## 不做（这轮明确排除）

- `state.py` 接线、`--iteration`、`status` 子命令、实例目录
- `runId`、`seq`、失败重试、增量落盘（崩溃仍丢日志；要改是另一份 plan）
- 图与预设的任何修改

## 风险

| 风险 | 处理 |
|---|---|
| 计时把模型解析也算进去（微秒级） | 忽略，不影响结论 |
| `perf_counter` 在 Windows 上精度 15ms 级 | 影响可忽略；只用于毫秒统计 |
| 失败路径多写一笔，可能打乱依赖顺序的断言 | 仅在 `except` 分支追加，正常路径顺序不变 |
| 记录变长 | 每行 +~70 字节，一轮约 40 条 → +3 KB，可忽略 |

## 验证

- `python -m unittest discover -s agents-workflow-engine/tests` → 28/28
- `./.agents/verify.sh` → 68 项全绿
- 手工：`--project <临时目录> run`（假 agent）后逐行看 `decisions.jsonl`，确认 `durationMs` 为正且与 `startedAt` 递增一致
