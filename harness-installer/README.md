# harness-installer

为任意项目铺好 **工程底座**：`AGENTS.md` + `docs/` 文档骨架 + `opencode.jsonc`。

```
harness-installer/
├── SKILL.md
├── scripts/init-harness.sh
└── templates/
    ├── AGENTS.md.template      # 架构与工程规范模板（含 TODO 占位）
    ├── opencode.jsonc
    └── docs/
        ├── README.md
        ├── architecture/       # C4 / ADR / 术语 / 产品 / 核心领域 / 迭代规划
        ├── features/           # _template/{spec,plan}.md + _chores/
        ├── facts/              # as-built 事实 + business/ + tech-topic/
        ├── standards/          # architecture / layers / naming / test 预置
        │   └── templates/      # 代码模版 / ADR 模板（预置）
        └── test-cases/
            ├── e2e-cases/test-cases.md
            ├── manual-cases/manual-test-cases.md
            ├── smoking-cases/smoking-test-cases.md
            └── dev-self-cases/README.md
```

`docs/standards/` 里只预置四份不分技术栈就能写的规范（architecture / layers / naming / test）；
`api-design / db / error / security / business-rule / data-dictionary` 在对应能力落地时再建，
不要留空壳假装有规范（细则见 `templates/docs/standards/README.md`）。

## 用法

```bash
# 预览
./harness-installer/scripts/init-harness.sh ../my-project --dry-run

# 执行
./harness-installer/scripts/init-harness.sh ../my-project

# 渲染成项目相对路径（产物可随仓库分发，与 agile-team-sdd 的 PATH_MODE 一致）
PATH_MODE=relative ./harness-installer/scripts/init-harness.sh ../my-project

# 强制覆盖
./harness-installer/scripts/init-harness.sh ../my-project --force
```

| 环境变量 | 说明 |
|---|---|
| `PATH_MODE=absolute`（默认） | 产物写绝对路径，agent 在任意 cwd 下可用 |
| `PATH_MODE=relative` | 产物写项目相对路径；要求 agent 的 cwd 在项目根 |
| `BACKEND_DIR` / `FRONTEND_DIR` / `DOCS_DIR` / … | 覆盖目录探测结果 |
| `TECH_STACK` / `BACKEND_DESC` / `DATABASE` / … | 填进 `AGENTS.md` 描述，减少手工 TODO |

## 脚本做了什么

1. 探测项目结构：`containers/backend/`（`pom.xml`）、`containers/frontend/`（`package.json`）、`e2e/`、`docs/`
2. 渲染 `templates/AGENTS.md.template` → `<项目>/AGENTS.md`
3. 渲染 `templates/docs/**` → `<项目>/docs/**`（模板里的 `{{...}}` 按 `PATH_MODE` 展开）
4. 缺失时创建 `<项目>/opencode.jsonc`

已存在的文件默认跳过，重复执行安全。

## 生成的 AGENTS.md 是"半成品"

模板里的 `TODO` 段落需要项目负责人补全。参考实现见
[`../example-project/AGENTS.md`](../example-project/AGENTS.md)。
