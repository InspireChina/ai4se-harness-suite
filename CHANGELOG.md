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

## [0.4.0] - 2026-11-20

把项目准备的架构职责拆成两半：BA 立业务意图，TL 接技术架构。

- **新增 `ba-arch-plan`**（BA 组，第 27 个 skill）：起草 `docs/architecture/business/`
  的产品边界、术语基线、核心聚合、迭代规划，并给出「核心聚合 → 建议容器」交接表给 TL
- **`tl-arch-plan` 收窄到技术侧**：只管 `tech/`（C4 上下文/容器、ADR），`business/` 只读；
  容器切分依据必须是业务侧的核心聚合，而不是代码目录
- **顺序固定**：BA 先 → TL 后 —— 先画 C4 再定业务边界，图必重画
- **骨架同步**：`harness-installer` 模板里 `architecture/README.md`、`business/*.md` 的「维护：」
  与 `AGENTS.md.template` 的目录注释都改成两支 skill
- **guide**：矩阵「项目准备」拆成 BA 业务架构 / TL 技术架构两行；接入顺序、出口条件、角色手册同步；
  `flow.html` 在 BA 泳道加「业务架构意图」节点，阶段边界顺延一列
- **安装器 `--manifest-only`**：目标项目里文档已被填过、不该被 `--force` 覆盖时，用它只把
  `.agents/harness/<模块>.json` 升到当前套件版本（模板改动由人手工同步）；三个安装器同步支持
- **`--help` 修正**：`install-tools.mjs` 之前把 `//` 前缀原样打出来，且漏了 `--list`

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