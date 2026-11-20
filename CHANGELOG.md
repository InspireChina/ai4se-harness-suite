# 变更记录（套件）

本文件记 **整个 harness 套件** 的版本。仓库根 [`VERSION`](VERSION) 是唯一事实源，两者必须相等
（`./.agents/verify.sh` 第 13 节会检查）。

只有两个模块自带版本号，它们记的是自己的兼容面，不跟随本文件的编号：

| 模块 | 版本源 | 为什么要单独编号 |
|---|---|---|
| `agents-workflow-engine` | [`agents_workflow_engine/version.py`](agents-workflow-engine/agents_workflow_engine/version.py) + [CHANGELOG](agents-workflow-engine/CHANGELOG.md) | 引擎会被整目录复制进目标项目并有自己的预设格式代次（`__schema__`） |
| `overnight-runner` | `overnight_runner/__init__.py` 的 `__version__` | 同样是整目录复制走的运行时 |

其余模块（`agile-team-sdd`、`harness-installer`、`tool-chain-installer`、`team-workflow-guide`）
跟随套件版本。

装进目标项目后，每个模块在 `.agents/harness/<模块>.json` 留一条清单，
记着自己的版本与安装时的套件版本 —— 这是「装的是哪一版、落后多少」的机器可读答案。

## [0.3.0] - 2026-11-20

给套件立一个版本号，并让每个模块装进目标项目时留下清单，能机器比对「装的是哪一版、差几个模块」。

- **套件版本**：新增根 `VERSION` 与本文件；`agents-workflow-engine` / `overnight-runner` 沿用各自的版本号
- **安装清单**：五个安装器都会写 `.agents/harness/<模块>.json`（`module` / `version` / `suite` / `installedAt`），
  一个模块一个文件，谁安装谁写自己那份，不需要合并
- **版本比较**：安装器发现项目里记着别的版本时在 stderr 提示；没加 `--force` 就不动清单，
  避免出现「文件跳过了、清单却升级了」
- **验证**：`verify.sh` 新增第 13 节 —— `VERSION` ↔ 本文件、`example-project` 的清单 ↔ 源码版本
- **已安装正文一致性**：第 6 节从「只比名字」改成「逐行比正文」（占位符按通配），模板改了没重装会被抓出来；
  同时补齐 `example-project` 里落后于模板的 3 个 skill（`qa-run-e2e` / `qa-write-cases` / `qa-write-manual-plan`）
- **修占位符正则**：占位符名带数字（`{{E2E_RUNNER}}` / `{{E2E_DIR}}` / `{{E2E_CASES_DIR}}`）之前不在
  `[A-Z_]+` 的覆盖范围里，残留检查与「已登记」检查都漏看它们；统一改成 `[A-Z0-9_]+`
- **修 `PATH_MODE` 未定义**：`agile-team-sdd/install.sh` 在 `PATH_MODE` 默认值之前就读了它，
  `set -u` 下直接报 unbound variable
- 模块版本：`agents-workflow-engine` 0.2.0、`overnight-runner` 0.1.0

## 0.3.0 之前

没有套件版本号。各模块的改动只记在自己的 README 与 `agents-workflow-engine/CHANGELOG.md` 里。