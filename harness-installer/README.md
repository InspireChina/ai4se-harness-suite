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
        ├── features/_template.md
        ├── plans/_template.md
        ├── designs/README.md
        ├── designs/topic/README.md
        ├── standards/README.md
        ├── standards/templates/README.md
        └── test-cases/
            ├── README.md
            ├── e2e-cases/test-cases.md
            ├── manual-cases/manual-test-cases.md
            ├── smoking-cases/smoking-test-cases.md
            └── dev-self-cases/README.md
```

## 用法

```bash
# 预览
./harness-installer/scripts/init-harness.sh ../my-project --dry-run

# 执行
./harness-installer/scripts/init-harness.sh ../my-project

# 强制覆盖
./harness-installer/scripts/init-harness.sh ../my-project --force
```

## 脚本做了什么

1. 探测项目结构：`backend/`（`pom.xml`）、`frontend/`（`package.json`）、`e2e/`、`docs/`
2. 渲染 `templates/AGENTS.md.template` → `<项目>/AGENTS.md`
3. 复制 `templates/docs/**` → `<项目>/docs/**`
4. 缺失时创建 `<项目>/opencode.jsonc`

已存在的文件默认跳过，重复执行安全。

## 生成的 AGENTS.md 是"半成品"

模板里的 `TODO` 段落需要项目负责人补全。参考实现见
[`../example-project/AGENTS.md`](../example-project/AGENTS.md)。
