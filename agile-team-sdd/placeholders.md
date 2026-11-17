# 占位符字典（Placeholders）

`agile-team-sdd/skills/**/SKILL.md` 是 **模板**。其中所有项目相关的路径都写成 `{{PLACEHOLDER}}` 形式，
由 `install.sh` 在安装时替换为目标项目的真实绝对路径。

渲染时按 **从长到短** 的顺序替换（`PROJECT_ROOT` → `BACKEND_DIR` → `DOCS_DIR` → `PLANS_DIR`），
因此后置占位符可以安全地引用前置占位符。

## 占位符清单

| 占位符 | 含义 | 默认值（相对 `{{PROJECT_ROOT}}`） | 可用环境变量覆盖 |
|---|---|---|---|
| `{{PROJECT_ROOT}}` | 目标项目根目录（绝对路径） | —（安装参数） | `PROJECT_ROOT` |
| `{{PROJECT_NAME}}` | 项目名 | 根目录目录名 | `PROJECT_NAME` |
| `{{HARNESS_ROOT}}` | harness 套件源码根目录（`pm-retro` 回写用） | 安装脚本所在套件的根 | `HARNESS_ROOT` |
| `{{AGENTS_FILE}}` | 工程规范文件 | `AGENTS.md` | `AGENTS_FILE` |
| `{{SKILLS_DIR}}` | skills 安装目录 | `.agents/skills` | `SKILLS_DIR` |
| `{{MCP_CONFIG_FILE}}` | MCP 配置文件 | `.mcp.json` | `MCP_CONFIG_FILE` |
| `{{BACKEND_DIR}}` | 后端模块目录 | `containers/backend` | `BACKEND_DIR` |
| `{{FRONTEND_DIR}}` | 前端模块目录 | `containers/frontend` | `FRONTEND_DIR` |
| `{{E2E_DIR}}` | E2E 测试目录 | `e2e` | `E2E_DIR` |
| `{{DOCS_DIR}}` | 文档根目录 | `docs` | `DOCS_DIR` |
| `{{FEATURES_DIR}}` | 需求与方案根目录（feature 文件夹） | `docs/features` | `FEATURES_DIR` |
| `{{CHORES_DIR}}` | 无关联 feature 的横切 plan 目录 | `docs/features/_chores` | `CHORES_DIR` |
| `{{PLANS_DIR}}` | 同 `CHORES_DIR`（兼容旧名） | `docs/features/_chores` | `PLANS_DIR` |
| `{{FACTS_DIR}}` | 事实文档目录 | `docs/facts` | `FACTS_DIR` |
| `{{BUSINESS_FACTS_DIR}}` | 业务事实目录 | `docs/facts/business` | `BUSINESS_FACTS_DIR` |
| `{{TECH_TOPIC_DIR}}` | 技术专题目录 | `docs/facts/tech-topic` | `TECH_TOPIC_DIR` |
| `{{STANDARDS_DIR}}` | 代码规范目录 | `docs/standards` | `STANDARDS_DIR` |
| `{{TEST_CASES_DIR}}` | 测试用例文本基线根目录 | `docs/test-cases` | `TEST_CASES_DIR` |
| `{{E2E_CASES_DIR}}` | QA E2E 文本用例目录 | `docs/test-cases/e2e-cases` | `E2E_CASES_DIR` |
| `{{MANUAL_CASES_DIR}}` | QA 手动用例目录 | `docs/test-cases/manual-cases` | `MANUAL_CASES_DIR` |
| `{{SMOKING_CASES_DIR}}` | QA 冒烟用例目录 | `docs/test-cases/smoking-cases` | `SMOKING_CASES_DIR` |
| `{{DEV_SELF_CASES_DIR}}` | 开发自测用例索引目录 | `docs/test-cases/dev-self-cases` | `DEV_SELF_CASES_DIR` |
| `{{RELEASES_DIR}}` | 发布清单目录 | `docs/releases` | `RELEASES_DIR` |
| `{{SPEC_TEMPLATE}}` | 需求规格模板 | `docs/features/_template/spec.md` | — |
| `{{PLAN_TEMPLATE}}` | 技术方案模板 | `docs/features/_template/plan.md` | — |
| `{{DOMAIN_MODEL_DOC}}` | 领域模型文档 | `docs/facts/domain-model.md` | — |
| `{{API_SPEC}}` | API 定义 | `docs/facts/api.yaml` | — |
| `{{DB_SCHEMA_DOC}}` | 数据库规格 | `docs/facts/db-schema.md` | — |
| `{{BUSINESS_RULES_DOC}}` | 业务规则文档 | `docs/facts/tech-topic/businessrule.md` | — |
| `{{DATA_DICT_DOC}}` | 数据字典文档 | `docs/facts/tech-topic/data-dict.md` | — |
| `{{E2E_RUNNER}}` | 一键跑 E2E 的脚本 | `e2e-run.sh` | `E2E_RUNNER` |
| `{{TARGET_BRANCH}}` | 主干分支（MR 目标分支） | `main` | `TARGET_BRANCH` |
| `{{BACKEND_PORT}}` | 后端端口 | `8080` | `BACKEND_PORT` |
| `{{FRONTEND_PORT}}` | 前端端口 | `5173` | `FRONTEND_PORT` |
| `{{TEST_CMD_BACKEND}}` | 后端编译/测试命令 | `cd {{BACKEND_DIR}} && mvn test` | `TEST_CMD_BACKEND` |
| `{{TEST_CMD_FRONTEND}}` | 前端构建命令 | `cd {{FRONTEND_DIR}} && npm run build` | `TEST_CMD_FRONTEND` |

## 路径模式（`PATH_MODE`）

| 模式 | 渲染结果 | 何时用 |
|---|---|---|
| `absolute`（默认） | `/abs/path/to/project/docs/features/_chores/` | skill 在任意 cwd 下都要能用 |
| `relative` | `docs/features/_chores/` | 项目会随仓库分发给其他人（可移植） |

```bash
PATH_MODE=relative ./install.sh ../my-project
```

相对模式下 `{{PROJECT_ROOT}}` 渲染为 `.`，`{{HARNESS_ROOT}}` 仍为绝对路径
（它指向套件源码，在项目之外）。


## 不做替换的内容

以下内容视为 **项目无关**，安装时原样保留：

- `AGENTS.md` 章节号引用中的 `§14` 等编号（仅路径部分被替换）
- Markdown 代码块中的语言标注（`bash`、`yaml`、`plantuml` 等）
- `{{...}}` 之外的所有花括号内容（例如 PlantUML 的 `{字段}` 占位符）

## 渲染规则

1. 模板中每份 `SKILL.md` 顶部都带有一段 `<!-- TEMPLATE-ONLY --> ... <!-- /TEMPLATE-ONLY -->` 标记块，
   安装时会被整段删除，避免安装后的 skill 里出现"这是模板"的提示。
2. 模板的 frontmatter `name` 带 `-template` 后缀（如 `dev-plan-template`），安装时会改成最终名字
   （如 `dev-plan`），同时目标目录名也去掉后缀。这样模板与已安装的 skill 不会重名冲突。
3. 路径按 `PATH_MODE` 渲染：`absolute` 用绝对路径，`relative` 用项目相对路径。
4. 未识别的 `{{...}}` 会保留原样并在安装结束时报警，便于发现拼写错误。
