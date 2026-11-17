# Plan：docs/architecture 高阶设计（modify-example）

> 日期：2026-11-17  
> 状态：**已完成**

## 已拍板

- **领域模型双份**：`architecture/business/core-domain-model.md` = Core（核心聚合+关键字段）；`facts/domain-model.md` = as-built 全量（`ba-arch-sync-back` 对齐）
- **C4 文件名**：`c4-context.md` / `c4-container.md`
- **指南**：项目准备增加架构设计阶段（BA/TL → `docs/architecture/`）

## 目标树

```
docs/architecture/
├── README.md
├── tech/
│   ├── c4-context.md
│   ├── c4-container.md
│   └── adr.md   # 一句话决策表
└── business/
    ├── glossary.md
    ├── product.md
    ├── core-domain-model.md  # Core：核心聚合+关键字段
    └── iterations.md
```

## Skill

`tl-arch-plan` · `tl-arch-sync-back` · `ba-arch-sync-back`
