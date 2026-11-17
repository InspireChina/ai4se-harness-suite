# Feature 目录改为「文件夹 + spec/plan」

> 日期：2026-11-17
>
> 关联：案例项目 docs 结构继续优化
>
> **plan 一旦定稿就不修改。**

## 1. 目标

每个 feature 从「单个 `.md`」改为「一个文件夹」，内含：

| 文件 | 含义 |
|---|---|
| `spec.md` | 业务规格（原 feature 正文） |
| `plan.md` | 该需求的主技术方案（过程文档） |
| `plan-{slug}.md` | 同一需求的后续/并行方案（多份时） |

## 2. 提议命名（待确认前缀）

**默认提议**：文件夹名加 `feat-` 前缀。

```
docs/features/
├── _template/                      # 模板（原 _template.md）
│   ├── spec.md
│   └── plan.md
└── iteration1/                     # 迭代分组保留
    ├── README.md
    ├── prototypes/                 # 不动
    ├── feat-account/
    │   └── spec.md                 # 原 account.md
    ├── feat-booking/
    │   └── spec.md
    ├── feat-consultant-discovery/
    │   └── spec.md
    └── …
```

跨 feature / 基础设施类旧 plan（如 `20261106-fix-public-endpoints…`）本轮处理选项：

| 选项 | 做法 |
|---|---|
| A（推荐） | 仍留在 `docs/plans/`（横切 plan 目录保留） |
| B | 迁到 `docs/features/_shared/plan-{slug}.md` |
| C | 全部取消顶层 `docs/plans/`，横切也塞进某个 feat 或 `_shared` |

与 feature 明确相关的 iteration1 plan（`20261116-iteration1-*`）→ 放到 `iteration1/README` 旁或拆到各 feat；本轮可先放到 `iteration1/plan-{slug}.md`（迭代级，不是单 feat）。

## 3. 影响面

| 层 | 改动 |
|---|---|
| example-project | 搬家 + 改引用；`docs/features/_template`；AGENTS/README 文档树 |
| overnight-runner 队列 | `queue.yaml` 里 plan 路径若指向旧 `docs/plans/` 需更新 |
| agile-team-sdd | `ba-write-spec` 产出 `…/feat-{slug}/spec.md`；`dev-plan` 产出同目录 `plan.md` / `plan-{slug}.md` |
| placeholders | `SPEC_TEMPLATE` → `docs/features/_template/spec.md`；`PLAN_TEMPLATE` 新增；`PLANS_DIR` 语义变为「横切 plan」或废弃 |
| harness-installer | features/plans 模板骨架对齐 |
| catalog.json | `produces` 路径更新 |

## 4. 分阶段

1. **Phase A**：只改 `example-project`（搬家 + 引用）
2. **Phase B**：刷新 skill / 占位符 / 安装器 / 工作流指南

## 5. 已确认（2026-11-17）

1. 前缀：**大写字母编码**（JIRA 卡片风格），文件夹形如 `ACC-account/`
2. 横切 / 无关联 feature 的 plan → `docs/features/_chores/plan-{slug}.md`；取消顶层对「一切 plan」的依赖，可移除空的 `docs/plans/`（或仅作兼容说明）
3. **`iteration1/` 保留**；迭代级 plan → `iteration1/plan-{slug}.md`
4. 先 example-project，再刷 harness 模板
