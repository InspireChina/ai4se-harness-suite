# 命名规范

命名是评审的判定依据：**同类东西必须同名同形**。技术栈相关部分按实际改写，未定项留 `TODO`。

## 通用

- 一个概念在全项目只有一个名字；改了名字要同步 `{{GLOSSARY_FILE}}`
- 缩写只在团队共识时使用（`id`、`url`、`api`），不要自造缩写
- 禁止 `tmp`、`data1`、`newXxx`、`XxxHelper2` 这类无意义后缀

## 后端

| 类型 | 约定 | 示例 |
|---|---|---|
| Controller | `XxxController` | `OrderController` |
| 应用服务 | `XxxService` / `XxxAppService` | `OrderService` |
| 领域对象 | 业务名词，不加后缀 | `Order`、`OrderItem` |
| 值对象 | `XxxStatus`、`XxxId`、`XxxCode` | `OrderStatus` |
| 仓储接口 | `XxxRepository` | `OrderRepository` |
| 仓储实现 | `XxxRepositoryImpl` | `OrderRepositoryImpl` |
| 入参 DTO | `XxxCommand` / `XxxRequest` | `CreateOrderCommand` |
| 出参 DTO | `XxxResponse` | `OrderDetailResponse` |
| DTO 转换 | `XxxAssembler` | `OrderAssembler` |
| 持久化对象 | `XxxPO` | `OrderPO` |
| 持久化转换 | `XxxConverter` | `OrderConverter` |
| 数据访问 | `XxxMapper` / `XxxDao` | `OrderMapper` |
| 领域服务 | `XxxDomainService` | `PricingDomainService` |
| 异常 | `XxxException`，业务异常继承 `BusinessException` | `OrderAlreadyPaidException` |
| 包名 | 全小写，按分层组织 | `domain.aggregate`、`adapter.rest` |

- 方法名用动词开头：`createOrder`、`cancelOrder`、`listByStatus`
- 布尔返回值以 `is` / `has` / `can` 开头：`isPaid()`、`canCancel()`

## 前端

| 类型 | 约定 | 示例 |
|---|---|---|
| 组件 / 视图文件 | PascalCase `.vue` | `OrderList.vue` |
| Service 文件 | camelCase `.ts` | `orderService.ts` |
| Store 文件 | camelCase `.ts` | `orderStore.ts` |
| Composable | `useXxx.ts` | `useOrderFilter.ts` |
| 目录名 | kebab-case | `order-center/` |
| 路由路径 | kebab-case，名词复数 | `/orders/:id` |
| 变量 / 方法 | camelCase | `currentOrder`、`fetchOrders()` |
| 组件 props（模板中） | kebab-case | `:order-id="..."` |
| 事件名 | kebab-case | `@order-cancel` |
| 常量 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE` |

## 数据库

TODO：按选型补齐（本节按通用 SQL 数据库写）

- 表名小写蛇形、单数：`order`、`order_item`
- 字段小写蛇形：`created_time`、`unit_price`
- 主键统一 `id`；外键 `<表名>_id`：`order_id`
- 唯一索引 `uk_<表>_<列>`；普通索引 `idx_<表>_<列>`
- 迁移脚本按 `{{STANDARDS_DIR}}/db.md` 的命名

## API 路径

- 统一前缀 `/api/<版本>/<资源复数>`：`/api/v1/orders`
- 子资源用嵌套：`/api/v1/orders/{id}/items`
- 动作用子路径或独立资源，不在路径里写动词：`/api/v1/orders/{id}/cancel`
- 分页参数统一 `page` / `size`（或 `offset` / `limit`，全项目只选一种）

## 文档与文件

- 文档：`kebab-case.md`；用例：`TC-xxx`
- ADR：`ADR-xxx`，正文一句话进 `{{ADR_FILE}}`
- 迭代目录：`{{FEATURES_DIR}}/<迭代>/<CODE>-<slug>/`
