# C4 系统上下文（集成架构）

> 层次：Context — 本系统与外部用户/系统的边界。  
> 维护：`tl-arch-plan`；与实现漂移时用 `tl-arch-sync-back` 核对。

## 说明

咨询师预约平台（Consultation Platform）对终端用户、咨询师、管理员提供 Web 能力；外部依赖支付网关与短信通道（样例期可 Mock）。

## 图

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

LAYOUT_WITH_LEGEND()

Person(user, "终端用户", "预约咨询、评价、管理资料")
Person(consultant, "咨询师", "入驻、档期、履约、结算")
Person(admin, "管理员", "审核、治理、运营配置")

System(platform, "咨询师预约平台", "检索、预约、履约、结算与治理")

System_Ext(pay, "支付网关", "收款 / 退款 / 回调")
System_Ext(sms, "短信通道", "验证码投递")

Rel(user, platform, "使用", "HTTPS")
Rel(consultant, platform, "使用", "HTTPS")
Rel(admin, platform, "使用", "HTTPS")
Rel(platform, pay, "下单/退款/验签", "HTTPS")
Rel(platform, sms, "发送验证码", "HTTPS/API")

@enduml
```

## 集成要点

| 外部系统 | 方向 | 备注 |
|---|---|---|
| 支付网关 | 出站下单 + 入站回调 | 幂等与验签见 PLT |
| 短信通道 | 出站 | ACC 样例可用 Mock；生产替换实现 |
