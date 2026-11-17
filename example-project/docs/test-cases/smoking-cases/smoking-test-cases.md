# 冒烟用例 — 咨询预约平台

> **归属：QA 测试。** 发版前必须全绿的一组最小用例集。
> 目标：**5 分钟内跑完**，用于快速判断"能不能发"。
> 自动化实现位于 `e2e/tests/qa/app.spec.ts`，本文件是它的精简视图。

## 用例清单

| # | 用例 | 冒烟点 | 预期 | 自动化 |
|---|---|---|---|---|
| TC-S01 | 服务启动 | 后端可启动、前端可加载 | 无启动错误，首页 200 | `qa/app.spec.ts` → Public Pages |
| TC-S02 | 登录 | 管理员正确凭据登录 | 跳转到 `/admin/dashboard` | `qa/app.spec.ts` → Auth |
| TC-S03 | 用户注册 | 全新邮箱注册 | 跳转到 `/user/dashboard`，显示用户名 | `qa/app.spec.ts` → Auth |
| TC-S04 | 核心预约链路 | 选咨询师 → 选时间 → 提交 | 预约成功，出现在预约列表 | `qa/app.spec.ts` → User Flows |
| TC-S05 | 管理端可读 | 管理员查看用户/预约/网点列表 | 三个列表均正常渲染 | `qa/app.spec.ts` → Admin Flows |
| TC-S06 | 数据库连通 | 写入后可读回 | 无连接错误，数据一致 | `qa/app.spec.ts` |

## 执行

```bash
cd e2e && npm run test:qa
```
