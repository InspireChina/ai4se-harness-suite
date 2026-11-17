# example-project 目录结构调整 + harness 同步

> 日期：2026-11-17
>
> 关联需求：案例项目目录规范化（apps 多组件、runner 收敛、facts/business）
>
> **plan 一旦定稿就不修改。** 二次改造新建 `YYYYMMDD-{slug}.md`。

## 1. 文档说明

### 1.1 背景

- 案例项目根目录扁平：`backend/`、`frontend/` 与文档/工具混在一起，后续难再塞组件或 submodule。
- overnight-runner 代码装在 `tools/overnight-runner/`，配置与队列在 `.overnight-runner/`，分裂两处。
- `docs/designs/` 名义是「设计」，实际是事实文档；缺「业务事实」专区，与 `ba-gen-facts` 语义也不齐。

### 1.2 目标

1. **Phase A（本轮先做）**：只改 `example-project/` 目录与其内部引用。
2. **Phase B（随后）**：刷新 harness 安装器、占位符、skill 模板、根文档，使新装项目默认对齐 Phase A。

### 1.3 技术边界

- 不改业务代码逻辑；只搬家 + 改路径引用。
- 历史已定稿 Plan 正文：批量替换路径字符串以保链接可用，不改任务语义。
- overnight-runner **全部**（代码、启动脚本、`overnight-runner.yaml`）迁入 `.overnight-runner/`。
- `docs/designs/topic/` 重命名为 `docs/facts/tech-topic/`；占位符 `DESIGNS_DIR` → `FACTS_DIR`。

------

## 2. 目标目录结构

### 2.1 example-project（Phase A 完成后）

```
example-project/
├── apps/
│   ├── backend/                 # 原 backend/
│   └── frontend/                # 原 frontend/
├── docs/
│   ├── features/
│   ├── plans/
│   ├── facts/                   # 原 designs/
│   │   ├── business/            # 业务事实（新增）
│   │   │   ├── README.md
│   │   │   └── booking-flow.md  # 从 designs/ 根迁入
│   │   ├── api.yaml
│   │   ├── db-schema.md
│   │   ├── domain-model.md
│   │   ├── README.md
│   │   └── tech-topic/          # 技术专题（原 designs/topic/）
│   ├── standards/
│   └── test-cases/
├── e2e/
├── e2e-run.sh                   # 路径改为 apps/*
├── .overnight-runner/
│   ├── overnight_runner/        # Python 包
│   ├── overnight-runner         # 启动脚本
│   ├── overnight-runner.cmd
│   ├── overnight-runner.yaml    # 运行配置（自项目根迁入）
│   ├── project.yaml
│   └── queue/
├── AGENTS.md / README.md / …
└── （删除 tools/ 与根 overnight-runner.yaml）
```

### 2.2 facts 分层约定

| 位置 | 放什么 | 谁维护 |
|---|---|---|
| `docs/facts/` 根 | 可从代码校准的技术事实：`api.yaml`、`db-schema.md`、`domain-model.md` | `ba-gen-facts` + 开发 |
| `docs/facts/tech-topic/` | 技术专题 ADR / 实现说明（分层、JWT、错误码、`businessrule`、`data-dict` 等） | 开发 / TL |
| `docs/facts/business/` | 业务事实：流程等（本轮迁入 `booking-flow.md`） | BA / 开发 |

### 2.3 overnight-runner 布局

```
.overnight-runner/
├── overnight_runner/        # Python 包（可提交）
├── overnight-runner         # bash 入口
├── overnight-runner.cmd
├── overnight-runner.yaml    # runner 配置（自根迁入）
├── project.yaml
└── queue/<name>/…
```

启动：`.overnight-runner/overnight-runner run`

加载顺序：优先 `.overnight-runner/overnight-runner.yaml`；若仅根目录有旧文件则自动迁入（幂等）。

`.gitignore` 继续只排除 queue 运行时产物，**不**忽略包代码与启动脚本。

------

## 3. Phase A：example-project 改动清单

| # | 动作 | 细节 |
|---|---|---|
| A1 | `mkdir apps`；`git mv backend frontend apps/` | 保留历史 |
| A2 | `git mv docs/designs docs/facts`；建 `facts/business/`；迁 `booking-flow.md` | 补 `business/README.md`、改 `facts/README.md` |
| A3 | 将 `tools/overnight-runner/*` 迁入 `.overnight-runner/`；删空 `tools/` | 启动脚本路径仍用自身 `dirname`，一般不用改 |
| A4 | 改路径引用 | 见下表 |
| A5 | 更新已安装 skills（`.agent/skills/**`）里的绝对/相对路径 | Phase B 用 `install.sh --force` 再刷一遍更稳；Phase A 先改活文档 + 关键脚本 |

### A4 必须改的引用面

| 文件 | 改什么 |
|---|---|
| `e2e-run.sh` | `apps/backend`、`apps/frontend` |
| `.gitignore` | `apps/frontend/dist/`、`apps/backend/.../application.yml` 等 |
| `AGENTS.md` / `README.md` | 拓扑、命令、文档树 |
| `docs/README.md`、`docs/standards/*`、`docs/test-cases/**` | `designs`→`facts`，`backend`→`apps/backend` |
| 活着的 features / 非历史约束的说明 | `frontend/` → `apps/frontend/` |
| 历史 plans | 路径字符串批量替换（定稿不改语义） |

不改：Java/Vue 源码包结构、端口、Maven/npm 工程内部路径。

### Phase A 验证

```bash
test -d example-project/apps/backend
test -d example-project/apps/frontend
test -d example-project/docs/facts/business
test ! -e example-project/tools
test -x example-project/.overnight-runner/overnight-runner
grep -R 'docs/designs' example-project --include='*.md' --include='*.sh' | grep -v docs/plans/ || true
# 允许历史 plan 已替换完后上述为空
./scripts/verify.sh
```

（本仓库不强制跑 `mvn test` / Playwright。）

------

## 4. Phase B：harness / skill 同步（A 确认并落地后再做）

| 模块 | 改动 |
|---|---|
| `agile-team-sdd/placeholders.md` | `BACKEND_DIR`/`FRONTEND_DIR` 默认改为 `apps/backend`、`apps/frontend`；`DESIGNS_DIR` → **`FACTS_DIR`**（`docs/facts`）；新增 `BUSINESS_FACTS_DIR`（`docs/facts/business`）；派生文档路径随之改 |
| `agile-team-sdd/install.sh` | 同上默认值与替换字典；残留检查覆盖新名 |
| `agile-team-sdd/skills/*-template/` | 所有 `{{DESIGNS_DIR}}` / `docs/designs` 文案改为 facts；`ba-gen-facts` 等输出目录对齐 |
| `agile-team-sdd/{SKILL,README,catalog}.json/md` | 表格与示例树 |
| `harness-installer/` | 模板 `docs/designs` → `docs/facts` + `facts/business/`；探测逻辑优先 `apps/backend`、`apps/frontend`（兼容旧根目录） |
| `overnight-runner/scripts/install.sh` | `TARGET_TOOLS`：`tools/overnight-runner` → `.overnight-runner`；文档与完成提示 |
| `overnight-runner/{README,SKILL,docs/design}.md` | 布局图 |
| 根 `AGENTS.md` / `README.md` / `team-workflow-guide/index.html` | 流程与路径表 |
| `example-project/.agent/skills/` | `PATH_MODE=relative ./install.sh example-project --force` 重装 |

### Phase B 验证

```bash
./scripts/verify.sh
# overnight-runner 若改 install 行为：相关冒烟/单元仍绿
PATH_MODE=relative agile-team-sdd/install.sh example-project --force --dry-run
```

------

## 5. 已确认决策（2026-11-17）

1. Phase 分两步：先 A 后 B —— **同意**
2. 保留 topic，重命名为 `tech-topic`；`business/` 本轮迁入 `booking-flow.md` —— **同意**
3. overnight-runner **全部**迁进 `.overnight-runner/`（含 yaml）—— **同意**
4. 占位符 `DESIGNS_DIR` → `FACTS_DIR` —— **同意改名**

------

## 6. 非目标

- 不引入真实 submodule（只留 `apps/` 扩展位）。
- 不把 `e2e/` 迁入 `apps/`。
- 不改 overnight-runner 运行时状态机 / 决策逻辑。

## 7. 文档同步检查

- [ ] Phase A：`example-project` 文档与结构
- [ ] Phase B：套件清单 / 占位符 / 安装器 / 工作流指南 / 根 AGENTS.md
