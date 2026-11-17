---
name: modify-harness
description: 先优化 harness（模板、占位符、安装器、skill），再安装刷新到 example-project。当用户说"改 harness"、"改模板"、"改占位符"、"优化安装器"、"刷新 example 上的 skills"、modify-harness 时使用。
---

# 改 harness → 刷新 example

**方向**：harness 交付物是事实源 → 改完后 **强制重装** 到 `example-project/`，保证样例与套件一致。

适用于：skill 模板正文、占位符、catalog、安装脚本、docs 骨架模板、overnight-runner 安装布局等。

## 什么时候用

- 优化 / 修复 harness 本身（不是先在业务样例里试约定）
- 用户明确说「改模板 / 安装器 / skill，再刷到 example」
- 只改套件文档或触发描述，也需要重装时验证 example 仍干净

**不要用本 skill**：要以样例试出新目录/文档约定再推广（用 `modify-example`）。

## 硬性约束

1. **Plan 闸门**：在 `.agents/plan/YYYYMMDD-{slug}.md` 写方案，**等人确认**后再动手（纯文案微调且用户说跳过闸门除外）。
2. **模块边界**：`agile-team-sdd` / `harness-installer` / `tool-chain-installer` / `overnight-runner` **互不 import**。
3. 新增占位符必须登记 `agile-team-sdd/placeholders.md`；模板带 `TEMPLATE-ONLY` 块；`name` 与目录一致且模板带 `-template` 后缀。
4. 安装脚本保持：`--help` / `--dry-run`、幂等、默认不覆盖、产物无安装机绝对路径。
5. 改完：`PATH_MODE=relative` 重装 example skills，再跑 `./.agents/verify.sh`。

## 怎么做

### 1. 确认落点模块

| 改动类型 | 改哪里 |
|---|---|
| SDD skill 行为 / 触发词 | `agile-team-sdd/skills/<name>-template/` + `catalog.json` + 套件 `SKILL.md`/`README.md` |
| 路径 / 默认目录 | `placeholders.md` + `install.sh`（及 `harness-installer/scripts/init-harness.sh` 若相关） |
| 目标项目 docs / AGENTS 骨架 | `harness-installer/templates/` |
| MCP 清单 | `tool-chain-installer/catalog/mcp-catalog.json` |
| overnight-runner 安装位置 / 配置 | `overnight-runner/scripts/install.sh` + 包代码 / 测试 |
| 流程与角色叙述 | `team-workflow-guide/index.html`（测试分类同时看 `example-project/docs/standards/test.md`） |

### 2. Plan → 等人确认

写清：改哪些文件、是否破坏性（占位符改名、默认路径变更）、example 如何验证、是否需要 `--force` 重装。

### 3. 先写验证（若可自动化）

- 能加进 `./.agents/verify.sh` 或 overnight-runner 单测/冒烟的先加
- 破坏性约定变更：在 Plan 里写明迁移 / 兼容策略（旧路径自动迁？仅文档提示？）

### 4. 实现 harness 改动

- 模板路径一律 `{{PLACEHOLDER}}`
- 新增 skill：建 `skills/<name>-template/SKILL.md` → 登记 `catalog.json` → 更新套件表格
- 改 overnight-runner 行为：保持零第三方依赖与 Python 3.9 语法约束

### 5. 刷新到 example-project

先 dry-run，再强制安装：

```bash
PATH_MODE=relative ./agile-team-sdd/install.sh example-project --dry-run
PATH_MODE=relative ./agile-team-sdd/install.sh example-project --force

# 若改了 harness-installer 骨架且需要对照：
# ./harness-installer/scripts/init-harness.sh example-project --dry-run
# （对已填满的 example 慎用 --force，避免冲掉手写 AGENTS/docs）

# 若改了 overnight-runner 安装器：
./overnight-runner/scripts/install.sh example-project --force
```

**注意**：`init-harness.sh --force` 会覆盖目标 `AGENTS.md` / docs 模板文件；example 已是完整范例时，优先手改对齐或只重装 skills，除非 Plan 明确要求强刷骨架。

### 6. 对齐 example 手写层（若需要）

重装 skills **不会**自动改 `example-project/AGENTS.md`、业务 docs 正文。若 harness 约定变了而 example 手写层仍旧：

- 按新约定改 example 文档树 / AGENTS 相关章节
- 或开一轮 `modify-example` 专做样例对齐（在 Plan 里写明）

### 7. 验证与自检

```bash
./.agents/verify.sh
# 改了 overnight-runner 行为：不要 --fast
```

- [ ] 模板无残留未登记占位符
- [ ] example 已安装 skill 无 `{{...}}`、无本机绝对路径
- [ ] catalog ↔ 模板 ↔ 已安装一致
- [ ] §13 文档同步完成
- [ ] 提交说明含验证方式与文档同步检查

## 反模式

- 改完模板不 `--force` 重装 example，样例 skills 继续说旧路径
- 把 example 当安装器的输出随便 `--force` 冲掉手写 AGENTS，却不在 Plan 里声明
- 只改 `example-project/.agent/skills/` 已安装副本，不改 `*-template`（下次安装会盖回去）
- 跨模块直接 import 代码

## 相关

- 反向流程：`.agents/skills/modify-example/SKILL.md`
- 规范：根目录 `AGENTS.md`
- 验证：`./.agents/verify.sh`
