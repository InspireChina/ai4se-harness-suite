# 需求与方案（Features）

每个业务能力是一个 **JIRA 风格编码文件夹**，规格与技术方案放在一起：

```
docs/features/
├── _template/                 # 模板：spec.md + plan.md
├── _chores/                   # 无关联 feature 的横切 plan
│   └── plan-{slug}.md
└── iteration1/
    ├── README.md
    ├── high-level-design.md   # 迭代高阶技术设计（HLD / TRD，人工确认）
    ├── ACC-account/
    │   ├── spec.md            # 业务规格（引用 architecture/business/glossary.md）
    │   ├── plan.md            # 主技术方案（粗实施步骤；HLD 确认后）
    │   ├── plan-progress.md   # dev-build 细化进度（随实现更新）
    │   └── plan-{slug}.md     # 多份方案时（对应 plan-{slug}-progress.md）
    └── prototypes/            # 迭代原型（可选）
```

约定：每个迭代目录应有 `high-level-design.md`；**确认前不得写 feature Plan**。  
项目级术语表在 [`../architecture/business/glossary.md`](../architecture/business/glossary.md)；`spec.md` 在 §2 附近引用之。  
项目级架构意图在 [`../architecture/`](../architecture/)（C4、ADR、产品/领域）；迭代 HLD 继承之。  
Plan 只写粗「实施步骤」；`dev-build` 写同目录 `{planStem}-progress.md` 细 checklist 并勾选。

| 编码 | 文件夹 | 含义 |
|---|---|---|
| ACC | `ACC-account` | 账号 |
| BKG | `BKG-booking` | 预约下单 |
| CDC | `CDC-consultant-discovery` | 咨询师发现 |
| COB | `COB-consultant-onboarding` | 咨询师入驻 |
| CSC | `CSC-consultant-schedule` | 咨询师档期 |
| CFL | `CFL-consultant-fulfillment` | 咨询师履约 |
| SET | `SET-settlement` | 结算 |
| ADM | `ADM-admin-ops` | 管理运营 |
| PLT | `PLT-platform-capability` | 平台能力 |
