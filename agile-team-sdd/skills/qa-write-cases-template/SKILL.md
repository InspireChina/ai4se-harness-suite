---
name: qa-write-cases-template
description: 编写 QA 测试用例（TC-xxx 文本用例 + Playwright 自动化实现）。当需求规格已确认，需要把验收标准与业务规则转成可执行用例时使用。
---

<!-- TEMPLATE-ONLY -->
> **这是模板文件。** 路径由 `{{PLACEHOLDER}}` 占位符标记，执行 `agile-team-sdd/install.sh` 时会被替换为目标项目的真实路径。
<!-- /TEMPLATE-ONLY -->

# QA：编写测试用例

QA 用例验证 **系统符合需求规格**，判定权归 QA。它是 **合并闸门**。

| | QA 测试 | 开发自测 |
|---|---|---|
| 依据 | 需求规格 | Plan |
| 编号 | `TC-xxx` | 无 |
| 位置 | `{{E2E_CASES_DIR}}/`、`{{E2E_DIR}}/tests/qa/` | 源码旁、`{{E2E_DIR}}/tests/dev/` |
| 判定 | QA | 开发 |

## 顺序不能反

```
1. 先写文本用例   → {{E2E_CASES_DIR}}/test-cases.md
2. 再写自动化实现 → {{E2E_DIR}}/tests/qa/*.spec.ts
```

**反过来做会漏场景** —— 照着实现写断言，测的是"实现做了什么"，不是"需求要求什么"。

## 第一步：建覆盖矩阵

从需求规格抽出所有锚点，逐条映射：

| 规格来源 | 编号 | 对应用例 |
|---|---|---|
| 验收标准 | `AC-001` | `TC-001` |
| 业务规则 | `R-CREATE-001` | `TC-004` |
| 权限矩阵 | 角色 × 操作 | `TC-012` |

**每个锚点至少一条用例。** 有锚点没用例 = 覆盖缺口，不能进验收。

规格位置：`{{FEATURES_DIR}}/<迭代>/<CODE>-<slug>/spec.md`。

## 第二步：写文本用例

`{{E2E_CASES_DIR}}/test-cases.md`，格式：

```markdown
## 2. 认证

| # | 用例 | 步骤 | 预期 | 关联 |
|---|---|---|---|---|
| TC-006 | 管理员登录成功 | 填写 admin@test.com / password → 提交 | 跳转到 `/admin/dashboard`，显示"管理仪表盘" | AC-002, R-AUTH-001 |
| TC-007 | 错误密码提示 | 填写 admin@test.com / wrongpassword → 提交 | 显示错误提示 | AC-003 |
```

| 列 | 要求 |
|---|---|
| `#` | `TC-xxx`，全局唯一，不复用编号 |
| 用例 | 一句话说明场景 |
| 步骤 | 可执行的动作，**不含"点击那个按钮"这种模糊表述** |
| 预期 | **可观察的结果**，不是"正常工作" |
| 关联 | 对应的 `AC-xxx` / `R-xxx` |

编号规则：

- 编号 **不复用**：用例删掉了，编号作废，不给新用例用
- 编号 **连续分配**，便于看覆盖情况
- 手动用例用 `TC-Mxx`，冒烟用 `TC-Sxx`

## 第三步：写自动化实现

放在 `{{E2E_DIR}}/tests/qa/`：

```ts
test('TC-006 管理员登录成功', async ({ page }) => {
  await page.goto('/login')
  await page.fill('input[type="email"]', ADMIN_EMAIL)
  await page.fill('input[type="password"]', ADMIN_PASSWORD)
  await page.click('button[type="submit"]')
  await page.waitForURL('**/admin/dashboard', { timeout: 10000 })
  await expect(page.locator('h1')).toHaveText('管理仪表盘')
})
```

要求：

- **标题必须带编号**，与文本用例一一对应，可双向追溯
- 断言要 **具体**：断言文本值、URL、元素可见性，而不是"页面加载成功"
- **禁止硬等待**（`waitForTimeout`），用 `expect(...).toBeVisible()` 等显式等待
- 用例之间 **不能有顺序依赖**，各自准备数据
- 数据准备用共享 helper，不要复制粘贴

## 覆盖要求

| 类别 | 必须覆盖 |
|---|---|
| Happy Path | 每个主流程至少一条 |
| 参数错误 | 缺字段、类型错、超长、非法枚举值 |
| 权限 | 未登录、角色不足、越权访问他人数据 |
| 业务冲突 | 重复提交、时间/库存冲突、状态非法流转 |
| 边界 | 空列表、最大分页、临界值 |

## 自检清单

- [ ] 每个 `AC-xxx` / `R-xxx` 至少一条用例
- [ ] 文本用例与自动化用例编号一一对应
- [ ] 自动化标题带 `TC-xxx`
- [ ] 预期是可观察的具体结果
- [ ] 无硬等待
- [ ] 用例可独立重复执行
- [ ] 断言够强（不是"不为空"这种）
- [ ] `{{E2E_DIR}}/tests/qa/` 下 **只有** QA 用例，开发自测在 `tests/dev/`

## 运行

```bash
cd {{E2E_DIR}} && npm run test:qa
```

用例失败时用 `qa-run-e2e` 定位原因。
