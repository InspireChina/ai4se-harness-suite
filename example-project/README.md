# 咨询预约平台 / Consultation Booking Platform

全栈工程骨架（Java 17 / Spring Boot 3.2 / Vue 3 + TypeScript）。  
**业务实现已清空**；目标需求见 [`docs/features/iteration1/`](docs/features/iteration1/)。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Pinia + Vue Router 4 |
| 后端 | Java 17 + Spring Boot 3.2 + Spring Security + MyBatis-Plus 3.5 |
| 数据库 | MySQL 8.0 + Flyway 迁移 |
| 认证 | JWT（HMAC-SHA256）骨架 |
| 测试 | JUnit 5 + RestAssured / Playwright |

## 当前状态

- 后端：`GET /api/v1/health` + JWT / 异常处理 / 规则与字典框架空壳
- 前端：占位首页
- 需求与原型：`docs/features/iteration1/`（含独立 Vite 原型，端口 5174）
- 规范：`AGENTS.md`、`docs/standards/`

## 快速开始

### 后端

```bash
cd containers/backend
cp src/main/resources/application.yml.example src/main/resources/application.yml
# 填入 MySQL 密码与 JWT 密钥
mvn spring-boot:run
# http://localhost:8080/api/v1/health
```

### 前端

```bash
cd containers/frontend
npm install
npm run dev
# http://localhost:5173
```

### iteration1 原型（需求演示，非业务前端）

```bash
cd docs/features/iteration1/prototypes
npm install && npm run dev
# http://127.0.0.1:5174/
```

## 测试

```bash
cd containers/backend && mvn test
cd e2e && npm run test:dev   # 开发壳冒烟
cd e2e && npm run test:qa    # QA 闸门（用例待按 iteration1 重建）
```

## 文档

- **需求**：`docs/features/iteration1/`
- **事实**：`docs/facts/`（当前为空壳 as-built）
- **规范**：`docs/standards/`
- **清理方案**：`docs/features/_chores/plan-20261117-purge-demo-impl-for-iteration1.md`
