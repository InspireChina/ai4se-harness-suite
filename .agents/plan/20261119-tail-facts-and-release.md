# Plan：预设尾部补「刷新事实文档 → 准备上线」

> 日期：2026-11-19
> 状态：**已完成**（2026-11-19，验证：测试 25/25 · validate 28 节点 · verify.sh 68 项全绿）
> 范围：`agents-workflow-engine/presets/iteration-to-test.yaml` + `agents-workflow-engine/tests/test_units.py`
> 前置：预览图 `.agents/plan/iteration-to-test.html` 已改完（本轮完成，浏览器实检通过）
> 边界：**本轮不回写 / 不安装到 poc-company-a**，等项目那边演化定稿再统一收口

## 背景

预览图现在跑到 `人工补测 → 刷新事实文档 → 准备上线 → 可上线`，但引擎读的预设仍终止在
`accepted`（`kind: end`，标题「人工补测」）。图与引擎不一致，`graph` skill 按图推进时
会在人工补测处停住，`ba-gen-facts` / `dev-release-plan` 两个已装 skill 永远不被图调度。

这与 `AGENTS.md` §8 的数据流也不符——那里写的是：

```
→ ba-gen-facts（事实文档 docs/facts/ 同步）
→ …→ qa-run-e2e / qa-write-manual-plan（QA 验收，合并闸门）
→ dev-release-plan（上线清单 docs/releases/）
```

本轮只补 **两个节点**，不引入 `tl-arch-sync-back` / `ba-arch-sync-back` / `dev-create-mr` /
`pm-retro`（它们不在图的主干上，按需在 `overlay.yaml` 里挂）。

## 预设改动

### 节点（25 → 28）

`accepted` 让出终点位置，改成里程碑；新增两个 subagent 动作 + 一个新终点。

```yaml
  # 原：- { id: accepted, actor: master, kind: end, title: 人工补测 }
  - { id: accepted, actor: master, kind: milestone, title: 人工补测 }
  - { id: ba-gen-facts, actor: subagent, kind: action, skill: ba-gen-facts, title: 刷新事实文档, model: writer }
  - { id: dev-release-plan, actor: subagent, kind: action, skill: dev-release-plan, title: 准备上线, model: writer }
  - { id: shipped, actor: master, kind: end, title: 可上线 }
```

### 边（32 → 35）

```yaml
  - { id: accepted-to-facts, from: accepted, to: ba-gen-facts }
  - { id: facts-to-release, from: ba-gen-facts, to: dev-release-plan }
  - { id: release-to-shipped, from: dev-release-plan, to: shipped }
```

改完 `e2e-pass`（`test-decision → accepted`）不变，只是 `accepted` 之后继续走。

### 为什么是「改成里程碑 + 新终点」而不是再加一个终点

`validate.py` 硬性要求 **恰好一个 `end` 节点**（`if len(ends) != 1`），且 `end` 不能有出边。
若保留 `accepted` 为 end，两个新节点就是死节点，直接报错。
`milestone` 的校验是「actor 必须是 master、不能带 skill/options、恰好一条出边」——`accepted`
本来就满足前两条，加上 `accepted-to-facts` 后第三条也满足。

两类节点都不带 `skill`，所以 `happy_answers()` 不需要新增答案键，只有 `action` 会真的调子 agent。

## 测试改动

`agents-workflow-engine/tests/test_units.py`（现 24 个用例）：

| 位置 | 现在 | 改成 |
|---|---|---|
| 6 处 `assertEqual(end, "accepted")` | 终点是人工补测 | `assertEqual(end, "shipped")` |
| `test_render_shapes` 第 81 行 | `assertIn("accepted([人工补测])", text)` | `assertIn("accepted([人工补测 · 里程碑])", text)`，并补 `shipped([可上线])`、`ba-gen-facts(刷新事实文档)`、`dev-release-plan(准备上线)` |
| `test_cli_run_writes_decisions` 第 294 行 | `assertIn('"node": "accepted"', body)` | **不动**——里程碑仍会写 `{"node": "accepted", "event": "milestone"}` |

新增 1 个用例 `test_tail_runs_facts_then_release`：

```python
calls = []
end = Runner(load_preset(), happy_answers(), fake_agent(calls), "master", log).run()
self.assertEqual(end, "shipped")
order = [item[0] for item in calls]
self.assertLess(order.index("qa-run-e2e"), order.index("ba-gen-facts"))
self.assertLess(order.index("ba-gen-facts"), order.index("dev-release-plan"))
self.assertEqual(order[-1], "dev-release-plan")   # 收尾两个动作排在最后
```

（`accepted` 不调 agent，不进 `calls`，所以只断言相对顺序与「最后一个是 release」。）

## 验证

```bash
cd agents-workflow-engine
PYTHONPATH=. python3 -m unittest discover -s tests -q     # 期望 25/25
PYTHONPATH=. python3 -m agents_workflow_engine validate    # 期望「图有效：28 个节点」
PYTHONPATH=. python3 -m agents_workflow_engine render      # 目测尾部三个新节点
cd .. && ./.agents/verify.sh                               # 全绿
```

迁移到目标项目后再跑一次单步模式，确认 `status` 的待办节点会走到 `ba-gen-facts`：

```bash
./.agents/workflow/workflow validate
./.agents/workflow/workflow --project /tmp/wf-tail start --instance t1   # 走到底应停在 shipped
```

## 文档同步

| 文件 | 是否要改 | 说明 |
|---|---|---|
| `.agents/plan/iteration-to-test.html` | 不改 | 本轮已同步改完 |
| `agents-workflow-engine/README.md` | **已改** | 主线图尾部接上两节点；`milestone` 举例补「人工补测」 |
| `AGENTS.md` §8 + §1 拓扑 | **已改** | 职责从「跑到人工补测」改为「跑到可上线」 |
| 根 `README.md` 模块表 | **已改** | 同上 |
| `team-workflow-guide/index.html` | 不改 | 只提「上线清单」的产出与角色，没有「补测即结束」的表述 |
| `agile-team-sdd/catalog.json` | 不改 | 没有新 skill，两个 skill 都已存在 |
| `agents-workflow-engine/schema/graph.schema.json` | 不改 | `milestone` / `end` 已在枚举里 |

## 不做的事

- **不加 `dev-create-mr` / `pm-retro`**：主干到「可上线」为止，复盘与 MR 由人按需触发。
- **不改 `overlay.yaml`**：这是预设的默认形态，项目要裁就在 overlay 里 `disable`。
- **不拆 `dev-build` 内部六步**：封死节点，保持现状。
- **不动 `state.py`**：本次只改图数据，不碰调度语义。

## 风险

- 目标项目里已装的 `.agents/workflow/engine/` 是副本，回写后需要重新复制 `presets/`，
  否则那边仍是 25 节点的旧图。**本轮按确认的范围不回写 poc**，等那边演化定稿后统一同步。
- 若有项目的 `overlay.yaml` 里 disable 了 `accepted`，改完后终点会缺失、validate 报
  「必须恰好有一个终点」——这种项目要在 overlay 里把 `shipped` 一并接上。
