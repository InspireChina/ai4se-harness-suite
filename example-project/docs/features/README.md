# 需求与方案（Features）

每个业务能力是一个 **JIRA 风格编码文件夹**，规格与技术方案放在一起：

```
docs/features/
├── _template/                 # 模板：spec.md + plan.md + glossary.md
├── _chores/                   # 无关联 feature 的横切 plan
│   └── plan-{slug}.md
└── iteration1/
    ├── README.md
    ├── high-level-design.md   # 迭代高阶技术设计（HLD / TRD，人工确认）
    ├── ACC-account/
    │   ├── spec.md            # 业务规格
    │   ├── glossary.md        # 本 feature 双语术语表（统一语言）
    │   ├── plan.md            # 主技术方案（可选；HLD 确认后）
    │   └── plan-{slug}.md     # 多份方案时
    └── prototypes/            # 迭代原型（可选）
```

约定：每个迭代目录应有 `high-level-design.md`；**确认前不得写 feature Plan**。  
每个 feature 目录应有 `glossary.md`（中文 | 英文 | 说明）；`spec.md` 在 §2 附近引用之。

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
