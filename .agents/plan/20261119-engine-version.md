# 引擎版本号：让「能不能装到 poc」有一个可比的标识

## 目标

1. `agents-workflow-engine` 有一个**唯一事实源**的版本号，`--version` 能查、`decisions.jsonl` 能留痕
2. 一份 `CHANGELOG.md`，版本 → 变更摘要，一眼看出「这版能不能装」
3. README 里写清**装到 poc 的闸门**，把这次实测出的坑记下来

## 为什么需要

`poc-company-a/.agents/workflow/` 里那份引擎比本仓库新（多 `stepper.py` 与
`start / submit / status / instances`），且 `preset.yaml` 是旧版（`writer/reviewer` +
每个节点带 `model:`）。

刚改完的预设把 `model:` 全删了、改成全局 `executor/gate`。**只装预设不装引擎**，
旧引擎会找不到 `model:` 而退回主会话模型 —— 模型配置静默失效。
版本号就是防止这种「半套升级」的抓手。

## 改动

| 文件 | 改什么 |
|---|---|
| `agents_workflow_engine/version.py` | 新增，`__version__ = "0.2.0"`，唯一事实源 |
| `agents_workflow_engine/__init__.py` | 导出 `__version__` |
| `agents_workflow_engine/cli.py` | `--version` → `agents-workflow-engine 0.2.0` |
| `agents_workflow_engine/runner.py` | `run()` 先写一条 `{"event": "engine", "version": ...}` |
| `CHANGELOG.md` | 新增，0.1.0 / 0.2.0 两节 |
| `README.md` | 顶部版本行 + 「什么时候能装到 poc」三条闸门 |
| `scripts/install.sh` | 打印版本，装机时提示「预设与引擎要成对升级」 |
| `.agents/verify.sh` | 新增「version.py ↔ CHANGELOG 最新版本一致」 |
| `tests/test_units.py` | 断言日志首行带版本、`--version` 输出 |
| `AGENTS.md` | 检查清单加一条：改引擎行为 → bump 版本 + 补 CHANGELOG |

## 版本号约定

- 0.x 阶段，语义化但不承诺兼容：`0.2.0` = 提示词调用 + 两模型 + 两种模式
- **只改文档/预设注释不 bump**；改了引擎行为（入参、协议、日志字段、模型解析）就 bump
- 预设里**不写**版本字段：旧引擎不认识新字段，写了也没人检查

## 装到 poc 的三条闸门

- [ ] poc 独有的 `stepper.py` + 四个子命令回到本仓库（或明确决定不引入）
- [ ] 本仓库版本 ≥ poc 里那版（poc 副本看 `version.py`，0.1.x 没有这个文件）
- [ ] 用真 CLI 冒烟跑通一个节点（`run --agent '<真命令>'`）

## 验证

- `python3 agents-workflow-engine/tests/test_units.py` 全绿
- `./.agents/verify.sh` 全绿
- `python3 -m agents_workflow_engine --version` 与 README/CHANGELOG 一致

## 实施结果

- 版本定为 **0.2.0**：`version.py` 是唯一事实源，`--version` / `decisions.jsonl` 首行 /
  `prompts.md` 抬头都带上；`__schema__ = 2` 跟版本一起落在日志里
- `CHANGELOG.md`：0.1.0（补记）与 0.2.0 两节，0.2.0 开头直接写「能不能装到 poc：还不能」
- `.agents/verify.sh` 新增「version.py ↔ CHANGELOG 最新一节」一致性检查（第 12 节）
- `install.sh` 现在读目标项目的 `version.py` 并与本预设对比，不一致就写到 stderr：
  实测三种情况（无引擎 / 0.1.9 / 一致）输出都对
- 顺手修了验证脚本里三处 `sed 's/^/  \033[32m✔…'` 输出裸转义码的问题（BSD sed 不展开 `\033`）
- 单元测试 38 → 40 个用例，全绿；`./.agents/verify.sh` 72 项全通过
- 没动 poc；装到 poc 的三条闸门写在 README「什么时候能装到 poc」，第一条（回灌 stepper）未开始

踩到的坑：macOS bash 3.2 在 `"…（引擎 $VERSION）"` 里把 `）` 的第一个字节当成变量名，
报 `VERSION…: unbound variable`；紧跟中日韩标点的变量引用要写成 `${VERSION}`。