# 需求与方案（Features）

每个业务能力是一个 **JIRA 风格编码文件夹**，规格与技术方案放在一起：

```
docs/features/
├── _template/                 # 模板：spec.md + plan.md
├── _chores/                   # 无关联 feature 的横切 plan
│   └── plan-{slug}.md
└── iteration1/
    ├── README.md
    ├── ACC-account/
    │   ├── spec.md            # 业务规格
    │   ├── plan.md            # 主技术方案（可选）
    │   └── plan-{slug}.md     # 多份方案时
    └── plan-{slug}.md         # 迭代级方案（可选）
```

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
