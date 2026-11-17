# 需求与方案（Features）

每个业务能力是一个 **JIRA 风格编码文件夹**：

```
docs/features/
├── _template/           # spec.md + plan.md
├── _chores/             # 无关联 feature 的 plan-{slug}.md
└── <迭代>/
    └── <CODE>-<slug>/
        ├── spec.md
        ├── plan.md
        └── plan-{slug}.md
```
