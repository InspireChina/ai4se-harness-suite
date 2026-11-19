# 引擎 `run`：提示词调用 + 两个模型 + 启动问「用不用独立 agent」

术语先定：叫 **独立 agent**（拉起独立进程干活的那个 agent），不叫"真子 agent"——
有的 agent 自己内部还有子 agent，两种含义混在一起说不清。

## 目标（三条一起改，因为它们都在 `run` 的同一个入口上）

1. **调用方式**：不再拼 `--skill / --node / --task`，改成传一段**提示词**，skill 写在提示词里
2. **模型**：预设里只配两个 —— **执行者** 与 **门禁**，按节点 `kind` 自动分配
3. **启动询问**：`run` 起来先问「是否使用独立 agent」；不用就输出**执行清单**，不起任何进程

## 一、提示词调用

现在 `runner.py#L287-L309`：`<cmd> --skill dev-build --node dev-build --model writer [--task a]`。
`--skill` / `--node` / `--task` **不是任何真实 CLI 的参数**（qoder、claude、opencode 都没有），
所以现在必须为引擎写 wrapper。改成：

```
<cmd> "<提示词>"
```

提示词内容（按节点类型拼）：

```
[graph-master] 节点 dev-build · 构建与自测 · 模型 执行者（qoder-max）

用 skill `dev-build` 完成本节点。
skill 文件：.agents/skills/dev-build/SKILL.md
（能直接加载 skill 就用 skill；加载不到就直接读这个文件）

本批任务：<task>                      ← 只有 repeatsBatch 节点有
节点说明：
- 后端 TDD
- 前端 TDD
...

完成标准：
1. 只改当前项目内的文件
2. 结论写在标准输出，引擎只读 stdout
3. 门禁节点：最后单独一行输出「满意」或「不满意」     ← 只有 gate
4. 批量节点：每条任务单独一行 `TASK: <id>`           ← 只有 batch
```

- **skill 名 + 文件路径都给**：Qoder CLI 读 `.qoder/skills`、Claude 读 `.claude/skills`、
  本仓库装 `.agents/skills`，只写名字在多数 CLI 上都会失效
- **模型不靠提示词约束**：「你必须用 X 模型」没有强制力，对抗验证会变成假验证；
  模型仍走命令行 `--model`（`qoder -m`、`claude --model` 都支持）
- 模板占位符（可选）：`{prompt}` / `{model}` 就地替换；没写就把提示词追加到末尾、`--model` 追加到末尾
- `subprocess.run(..., cwd=project)` —— **修一个现有隐患**：现在子 agent 在引擎自己的 cwd 里跑，
  提示词里的相对路径会找不到文件
- `WORKFLOW_*` 环境变量保留，老 wrapper 还能用

## 二、两个模型，配在图里

```yaml
models:
  executor: { model: DeepSeek-V4.1-Flash-1017, env: MODEL_EXECUTOR }   # 执行者：所有 action 节点
  gate:     { model: GLM-5.3-Flash,           env: MODEL_GATE }       # 门禁：所有 gate 节点
```

- 取值顺序：`env` 有值用 `env` → 否则用 `model` → 都空则沿用 `--master-model` 并给警告
- 两个 `model:` 就是上面这两个默认值，改模型只改这一处；CI 里换模型用 `MODEL_EXECUTOR` / `MODEL_GATE` 覆盖，不碰文件
- 预设里 13 处 `model: writer|reviewer` **全部删掉**，改按 `kind` 推：
  `gate` → 门禁模型，其余执行型 → 执行者模型（现有预设正好是这个映射：2 个 gate、12 个 action）
- 节点级 `model:` **仍然支持**（overlay 想单独换某个节点时用），优先级最高
- 对抗验证检查简化：不再逐个比 `REVIEW_PAIRS` 里的节点对，直接比这两个全局模型；
  相等 → 警告「未做对抗验证」，`validate.py` 的 `REVIEW_PAIRS` 随之删除

## 三、启动问一句

| `run` 的条件 | 行为 |
|---|---|
| 给了 `--agent` | 独立 agent 模式，**不问**（脚本友好） |
| 给了 `--manual` | 清单模式，**不问** |
| 都没给 + 交互终端 | 问 `是否使用独立 agent（拉起独立进程执行）？[Y/n]`，回车=是 |
| 都没给 + 非 TTY | 清单模式，stderr 说明原因，**不阻塞等输入** |

清单模式（`manual`，即“不启用独立 agent”）：

- 引擎不 spawn 任何进程，但也不只是给人看的待办——它输出**给当前会话 agent 的指令序列**：
  每条提示词开头写清楚“你现扮演执行者 / 门禁；**如果这个 agent 能开子 agent，就为本节点起一个子 agent 去做；
  开不了就自己按 skill 干**”。能开就用对方的子 agent 能力并行/隔离，不能开就沿着图往下走。
- 复用 Runner 的图遍历，`agent` 回调换成「收集提示词 + 返回占位结果」
- `gate` 假定「满意」（指令里标注：本次假定通过；实际判定不满意就回对应的打回节点）
- `batch` 节点标注「会按 plan 拆批，逐个 `TASK` 重复执行」
- 产出 `.agents/workflow/prompts.md`：按执行顺序编号，每段带角色与模型名
- **不写 `decisions.jsonl`** —— 没执行就不能记成执行过

## 四、代码改动

| 文件 | 改什么 |
|---|---|
| `agents_workflow_engine/prompts.py`（新） | `build_prompt(graph, node, role, model, task) -> str`，纯函数 |
| `agents_workflow_engine/runner.py` | `spawn_agent()` 追加提示词 + `cwd`；`_resolve_model()` 按 kind 取两个模型；`_warn_pair()` 删掉，改启动时记一条 `model-check` |
| `agents_workflow_engine/cli.py` | `run` 加 `--manual`、启动询问、清单模式分支 |
| `agents_workflow_engine/validate.py` | 删 `REVIEW_PAIRS`，改双模型全局检查 |
| `presets/iteration-to-test.yaml` | `models` 换 executor/gate，删 13 处 `model:` |
| `tests/test_units.py` | 见下 |
| `README.md`（引擎） | `--agent` 段重写；新增「两个模型」「两种模式」两节 |

## 五、测试（先写）

| 用例 | 断言 |
|---|---|
| `build_prompt` · action | 含 skill 名、`.agents/skills/<name>/SKILL.md`、note 列表 |
| `build_prompt` · gate | 含「满意」「不满意」 |
| `build_prompt` · repeatsBatch | 含「本批任务」与 `TASK:` |
| `build_prompt` · 无 skill 节点 | 不出现 skill 段落，不崩 |
| 模型 | 默认两个（DeepSeek / GLM）不同 → 无警告；手动配成相同 → 「未做对抗验证」；`env` 覆盖 `model`；节点级 `model:` 仍优先；现有 `test_preset_valid_and_warns_when_model_unset` 改为断言「预设自带两个模型，默认无警告」 |
| `spawn_agent` | 假 agent 记 argv 与 pwd：无 `--skill`、提示词含 skill 名、cwd == `--project`；`{prompt}`/`{model}` 替换；非 0 退出仍抛 `GraphError` |
| `run --manual` | 生成 `prompts.md`、含每个 action 的提示词、写清“能开子 agent 就开、开不了自己干”、gate 有“假定通过”；**没有** `decisions.jsonl` |
| `run --agent` | 不询问、照常写 `decisions.jsonl`（改掉现在按 `$2` 取 skill 的假 agent） |
| 非 TTY + 无 `--agent` | 走清单模式，不卡在 input |

## 六、不做

- stepper / 实例目录 / 续跑（poc 那条演化线，本仓库不引）
- 耗时字段（`20261119-engine-node-duration.md`，另一轮）
- 装任何 CLI、安装到 poc

## 七、验证

```bash
cd agents-workflow-engine && python3 tests/test_units.py
./.agents/verify.sh
```

可选真实冒烟（要花 token，需你点头）：`--agent 'claude -p'` 跑一个 `dev-plan` 节点，
确认提示词真的能驱动它按 skill 干活并吐出 `TASK:`。

## 实施结果

- 新增 `models.py`（`role_of` / `model_of` / `resolve`）与 `prompts.py`（`build_prompt`）
- `spawn_agent()` 改成「提示词 + `cwd=project`」，`_argv()` 支持 `{prompt}` / `{model}`
- `Runner._check_models()` 取代 `_warn_pair()`；`validate.py` 删掉 `REVIEW_PAIRS` 与两份重复的 `_model_value`
- `run` 多了 `--manual` 与启动询问；清单模式写 `.agents/workflow/prompts.md`
- 预设：`models` 换 `executor` / `gate` 两个默认值，删掉 13 处节点级 `model:`
- 测试 25 → 38 个用例全绿；`./.agents/verify.sh` 70 项全通过
- 真实命令行冒烟：假 agent 记到的 argv 是 `-q --model <模型> <提示词>`，`pwd` 等于项目根，模型按 kind 分开（执行者 10 次 / 门禁 2 次）

> 后续调整：启动问句从 `[Y/n]` 改成了三选一（会话内开子 agent / 只用主会话 / 独立 agent），
> 见 [20261119-engine-default-session-subagent.md](20261119-engine-default-session-subagent.md)。
