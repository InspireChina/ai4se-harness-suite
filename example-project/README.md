# 咨询预约平台 / Consultation Booking Platform

基于 DDD 四层架构的全栈咨询预约单体应用，支持用户注册登录、咨询师浏览、预约管理及后台管理。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Pinia + Vue Router 4 |
| 后端 | Java 17 + Spring Boot 3.2 + Spring Security + MyBatis-Plus 3.5 |
| 数据库 | MySQL 8.0 + Flyway 迁移 |
| 认证 | JWT（HMAC-SHA256，jjwt 0.12） |
| 测试 | JUnit 5 + RestAssured + MariaDB4j / Playwright |

## 项目结构

```
├── apps/
│   ├── backend/                # Spring Boot 后端
│   └── frontend/               # Vue 3 前端
├── e2e/                        # Playwright E2E 测试
├── docs/
│   ├── features/               # 需求规格
│   ├── plans/                  # 技术方案
│   ├── facts/                  # 事实文档
│   │   ├── business/           # 业务事实
│   │   └── tech-topic/         # 技术专题
│   ├── standards/              # 代码规范
│   └── test-cases/             # 测试用例文本基线
├── .overnight-runner/          # 无人值守 runner（代码 + 配置 + 队列）
└── AGENTS.md                   # AI Agent 工程规范
```

## 环境要求

- Java 17+
- Node.js 18+ / npm 9+
- MySQL 8.0（或使用 MariaDB4j 自动启动本地实例）

## 快速开始

### 1. 配置后端

```bash
cd apps/backend
cp src/main/resources/application.yml.example src/main/resources/application.yml
# 编辑 application.yml，填入 MySQL 密码和 JWT 密钥
```

### 2. 启动后端

```bash
cd apps/backend
mvn spring-boot:run
# 后端启动于 http://localhost:8080
```

### 3. 启动前端

```bash
cd apps/frontend
npm install
npm run dev
# 前端启动于 http://localhost:5173，/api 请求自动代理到后端
```

## 测试

用例分两层：**开发自测**（对开发负责）与 **QA 测试**（对需求负责，合并闸门）。详见 [`docs/standards/test.md`](docs/standards/test.md)。

### 开发自测

```bash
cd apps/backend
mvn test
# 使用 MariaDB4j 自动启动临时 MySQL，无需手动建库

cd e2e
npm run test:dev
# 只跑开发自测的 E2E 用例（视觉冒烟等），不阻塞合并
```

### QA 测试（合并闸门）

```bash
cd e2e
npm run test:qa
# QA 验收用例集，与 docs/test-cases/e2e-cases/test-cases.md 的 TC-xxx 一一对应

# 一键启动前后端 + 执行全部 E2E
bash e2e-run.sh
```

## 架构概览

```
Client → Vue 前端 (:5173) → /api 代理 → Spring Boot 后端 (:8080) → MySQL
```

- **adapter**：协议转换与参数校验，不含业务逻辑
- **application**：用例编排，组合 domain 行为，管理事务边界
- **domain**：领域模型与业务不变量，不依赖任何基础设施
- **infrastructure**：持久化实现、安全配置、异常处理

## 文档

详见 [`docs/`](docs/) 目录：

- **需求规格**：`docs/features/iteration1/` — 咨询师预约平台样例（v0.1；独立 Vite 原型：`prototypes/`，`npm run dev` :5174）
- **技术方案**：`docs/plans/` — 技术实现方案与任务拆分
- **设计文档**：`docs/facts/` — API 定义、数据库设计、领域模型、技术主题
- **代码规范**：`docs/standards/` — 架构、命名、安全、分层等规范及代码模板
- **测试用例**：`docs/test-cases/{e2e,manual,smoking,dev-self}-cases/`
