# 需求与方案（Features）

每个业务能力是一个 **JIRA 风格编码文件夹**：

```
docs/features/
├── _template/           # spec.md + plan.md
├── _chores/             # 无关联 feature 的 plan-{slug}.md
└── <迭代>/
    ├── high-level-design.md   # 迭代高阶技术设计（HLD / TRD，人工确认）
    └── <CODE>-<slug>/
        ├── spec.md
        ├── plan.md            # HLD 确认后再写
        └── plan-{slug}.md
```

约定：每个迭代目录应有 `high-level-design.md`；**确认前不得写 feature Plan**。
