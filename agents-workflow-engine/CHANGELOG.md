# CHANGELOG · agents-workflow-engine

版本号唯一事实源：`agents_workflow_engine/version.py`。

约定：

- 改了**引擎行为**（入参、提示词协议、日志字段、模型解析、子命令）→ bump 版本 + 在这里加一节
- 只改文档、注释、预设里的标题措辞 → 不 bump
- **预设与引擎成对升级**：预设里的新字段旧引擎不认识，半套升级不报错，只会静默退化成「都用主会话模型」

## [0.2.0] - 2026-11-19

**能不能装到 poc：还不能**（缺 `stepper.py` 与 `start / submit / status / instances`，见 README「什么时候能装到 poc」）。

- 调独立 agent 改成**传提示词**：不再拼 `--skill / --node / --task`，skill 名与 `SKILL.md` 相对路径都写进提示词，
  换 CLI（qoder / claude / …）不用写包装脚本
- 模型只剩两个，配在图的 `models` 下：`executor`（默认 `DeepSeek-V4.1-Flash-1017`）/ `gate`（默认 `GLM-5.3-Flash`），
  按节点 `kind` 自动分配，环境变量 `MODEL_EXECUTOR` / `MODEL_GATE` 可覆盖
- 删掉 13 处节点级 `model: writer|reviewer`；节点上写具体模型名仍然覆盖角色
- 对抗验证检查简化为「执行者与门禁是不是同一个模型」，删掉 `REVIEW_PAIRS` 与两处重复的 `_model_value`
- `run` 启动给三个选项：会话内开子 agent（默认）/ 会话内只用主会话（`--solo`）/ 独立 agent（`--agent`）；
  前两种只写 `prompts.md`、不拉进程，选独立 agent 不给 `--agent` 直接报错；非交互终端按第一项走
- `--agent` / `--manual` / `--solo` 三选一，同时给两个报错
- 新增 `--manual`：不拉进程，把每个节点的提示词写成 `.agents/workflow/prompts.md`（给当前会话 agent 的指令序列）
- 子 agent 的 `cwd` 改成目标项目根（原来在引擎自己的目录，相对 skill 路径找不到）
- `--agent` 支持 `{prompt}` / `{model}` 占位符
- `decisions.jsonl` 第一行记 `{"event": "engine", "version": ..., "schema": ...}`
- 新增 `--version`
- 单元测试 25 → 40

## [0.1.0] - 2026-11-19

第一版可用：YAML 图 + `validate / resolve / render / run`，回路与上限、并行分支与汇入、
`batch` / `repeatsBatch`、`once`、`sealed`、人工输入节点。

- 调子 agent 走自定义参数 `--skill / --node / --model / --task`，需要一个认这套参数的包装脚本
- 模型两角色 × 两档：`models.writer / models.reviewer` + 节点级 `model: writer|reviewer`
- 没有版本号概念（本文件与 `version.py` 之前不存在，此版按仓库历史补记）