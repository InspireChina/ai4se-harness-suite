---
name: harness-installer
description: 初始化项目的工程 harness —— 生成/补齐 AGENTS.md（架构与工程规范）与 docs/ 文档骨架（features/plans/designs/standards/test-cases 等）。当用户说"初始化项目"、"生成 AGENTS.md"、"建文档骨架"、"harness 安装"、"新项目接入规范"时使用。
---

# Harness 初始化器

为一个项目铺好 **工程底座**：`AGENTS.md`（唯一权威工程约定）+ `docs/`（文档体系骨架）+ `opencode.jsonc`（工具配置）。

典型场景：

- 新项目接入团队规范，需要一份 `AGENTS.md` 和文档骨架
- `example-project` 这类参考项目的骨架被删了，需要重建
- 给新团队成员一个可运行的最小 harness

## 前置：先确认目标

安装前必须确认 **目标项目目录**（绝对路径）。用户没说清楚就用 `question` 工具问，
不要默认装到当前目录。

## 执行

```bash
# 从本 skill 所在目录执行
./harness-installer/scripts/init-harness.sh <目标项目目录> --dry-run   # 先预览
./harness-installer/scripts/init-harness.sh <目标项目目录>
```

| 参数 | 说明 |
|---|---|
| `--dry-run` | 只打印将要发生的改动，不写文件 |
| `--force` | 覆盖已存在的 `AGENTS.md` 与文档文件 |
| `--no-agents` | 只生成 `docs/` 骨架，不动 `AGENTS.md` |

脚本会：

1. **探测项目结构**：找后端（有 `pom.xml`/`build.gradle`）、前端（有 `package.json`）、E2E 目录
2. **渲染 `AGENTS.md`**：把模板里的 `{{...}}` 占位符替换成探测结果，写入 `<项目>/AGENTS.md`
3. **铺 `docs/` 骨架**：复制 `templates/docs/**` 到 `<项目>/docs/**`
4. **确保 `opencode.jsonc`**：不存在则创建（注册 `.agent/skills` 路径）

## 生成后必须做的事

`AGENTS.md` 里的 `TODO` 段落 **不会** 被自动填好，必须补全，否则规范形同虚设：

| TODO 段落 | 要写什么 |
|---|---|
| §1 仓库拓扑 | 真实技术栈、各模块职责、运行时形态 |
| §2 鉴权与用户上下文 | 认证方式、token 传递、当前用户获取方式、权限模型 |
| §3 标准分层 | 实际分层与包路径 |
| §5 持久化规则 | ORM / Mapper、主键策略、聚合装配方式 |
| §8 领域设计 | 核心聚合、业务规则引擎、数据字典注册方式 |
| §9 状态机 | 核心状态机图与守卫方法 |
| §10 测试规范 | 单元/集成/E2E 框架、数据库测试方案 |
| §11 前端规范 | 框架版本、状态管理、路由、HTTP 封装约定 |

可以用 `example-project/AGENTS.md` 作为 **填写范例** —— 那是本仓库里已经填好的完整版本。

## 幂等性

- 已存在的 `AGENTS.md` / 文档文件默认 **跳过**（不覆盖），只有 `--force` 才覆盖
- `opencode.jsonc` 已存在时 **不修改**
- 因此可以放心在已有项目上重复执行

## 相关

- `agile-team-sdd/` — 装 SDD skills（dev-plan / dev-build / dev-debug），应在 harness 初始化 **之后** 执行
- `tool-chain-installer/` — 装 MCP 工具链
- `team-workflow-guide/` — 团队角色与协作约定
