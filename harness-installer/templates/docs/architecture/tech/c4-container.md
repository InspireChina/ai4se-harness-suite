# C4 容器

> 层次：Container。维护：`tl-arch-plan`。迭代细化见各 `docs/features/iterationN/high-level-design.md`。

## 说明

TODO：列出可独立部署/运行的单元及其职责。

## 图

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

LAYOUT_WITH_LEGEND()

Person(user, "用户")

System_Boundary(system, "本系统") {
  Container(web, "Web", "TODO", "TODO")
  Container(api, "API", "TODO", "TODO")
  ContainerDb(db, "DB", "TODO", "TODO")
}

Rel(user, web, "使用", "HTTPS")
Rel(web, api, "API", "HTTPS")
Rel(api, db, "读写", "JDBC")

@enduml
```
