# 需求与方案（Features）

每个业务能力是一个 **JIRA 风格编码文件夹**：

```
docs/features/
├── _template/           # spec.md + plan.md + glossary.md
├── _chores/             # 无关联 feature 的 plan-{slug}.md
└── <迭代>/
    ├── high-level-design.md   # 迭代高阶技术设计（HLD / TRD，人工确认）
    └── <CODE>-<slug>/
        ├── spec.md
        ├── glossary.md        # 本 feature 双语术语表（统一语言）
        ├── plan.md            # 粗实施步骤；HLD 确认后再写
        ├── plan-progress.md   # dev-build 细化进度（随实现更新）
        └── plan-{slug}.md     # 对应 plan-{slug}-progress.md
```

约定：每个迭代目录应有 `high-level-design.md`；**确认前不得写 feature Plan**。  
每个 feature 目录应有 `glossary.md`（中文 | 英文 | 说明）；`spec.md` 在 §2 附近引用之。  
Plan 只写粗「实施步骤」；`dev-build` 写同目录 `{planStem}-progress.md` 细 checklist 并勾选。
