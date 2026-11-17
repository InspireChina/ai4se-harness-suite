# C4 系统上下文（集成架构）

> 层次：Context。维护：`tl-arch-plan`。

## 说明

TODO：一句话描述本系统与外部用户/系统的边界。

## 图

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

LAYOUT_WITH_LEGEND()

Person(user, "用户", "TODO")
System(system, "本系统", "TODO")
System_Ext(ext, "外部系统", "TODO")

Rel(user, system, "使用", "HTTPS")
Rel(system, ext, "集成", "HTTPS")

@enduml
```
