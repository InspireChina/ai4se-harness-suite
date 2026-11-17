# 需求与方案（Features）

每个业务能力是一个 **JIRA 风格编码文件夹**，规格与技术方案放在一起：

```
docs/features/
├── _template/             # 模板：spec.md + plan.md
├── _chores/               # 无关联 feature 的横切 plan
│   └── plan-{slug}.md
└── <迭代>/
    ├── README.md
    ├── high-level-design.md
    └── <CODE>-<slug>/
        ├── spec.md            # 引用 architecture/business/glossary.md
        ├── plan.md
        └── plan-progress.md
```

项目级术语表在 [`../architecture/business/glossary.md`](../architecture/business/glossary.md)。  
项目级架构意图在 [`../architecture/`](../architecture/)。  
约定：每个迭代目录应有 `high-level-design.md`；**确认前不得写 feature Plan**。
