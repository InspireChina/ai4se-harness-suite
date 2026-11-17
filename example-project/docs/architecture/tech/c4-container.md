# C4 容器

> 层次：Container — 可独立部署/运行的单元。  
> 维护：`tl-arch-plan`。迭代级细化见各 `docs/features/iterationN/high-level-design.md`。

## 说明

样例为 **单体后端 + SPA 前端 + MySQL**：后端四层 DDD（ADR-001），前端 Vue SPA，共享同一浏览器入口按角色路由。

## 图

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

LAYOUT_WITH_LEGEND()

Person(user, "终端用户 / 咨询师 / 管理员")

System_Boundary(platform, "咨询师预约平台") {
  Container(web, "Web SPA", "Vue 3 + Element Plus", "三端路由与交互")
  Container(api, "Backend API", "Spring Boot", "鉴权、领域、编排、持久化")
  ContainerDb(db, "MySQL", "关系库", "业务数据与 Flyway 迁移")
}

System_Ext(pay, "支付网关")
System_Ext(sms, "短信通道")

Rel(user, web, "浏览 / 操作", "HTTPS")
Rel(web, api, "JSON API", "HTTPS / JWT")
Rel(api, db, "读写", "JDBC")
Rel(api, pay, "支付", "HTTPS")
Rel(api, sms, "短信", "HTTPS")

@enduml
```

## 容器职责

| 容器 | 职责 | 不负责 |
|---|---|---|
| Web SPA | UI、路由、表单校验（体验层） | 业务权威规则 |
| Backend API | 鉴权、用例、领域规则、集成 | 页面布局 |
| MySQL | 持久化与迁移 | 业务逻辑 |

## 相关 ADR

见 [adr.md](./adr.md)（ADR-001 四层 DDD · ADR-004 JWT）。
