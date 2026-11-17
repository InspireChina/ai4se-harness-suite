import { test, expect } from '@playwright/test'

/**
 * ACC · 账号与个人中心 —— QA 验收用例自动化。
 * 文本用例基线：docs/test-cases/e2e-cases/test-cases.md（TC-001 ~ TC-009）
 *
 * 环境约定：
 *  - 短信验证码固定码 123456（后端 SMS_MOCK_FIXED_CODE）
 *  - 平台管理员种子账号 13900000000 / Admin@12345（后端 seed.admin.*）
 */

const FIXED_SMS_CODE = '123456'
const ADMIN_PHONE = '13900000000'
const ADMIN_PASSWORD = 'Admin@12345'
const DISPLAYABLE_CONSULTANT_ID = 'stub-consultant-001'

/** 每个用例用独立手机号，避免同号登录态互相干扰。 */
function randomPhone(): string {
  return '13' + String(Math.floor(Math.random() * 1_000_000_000)).padStart(9, '0')
}

async function agree(page) {
  // Element Plus 的原生 checkbox 不可见，点击可见文案即可切换
  await page.getByText('已阅读并同意《服务协议》与《隐私政策》').click()
  await expect(page.getByRole('checkbox')).toBeChecked()
}

async function login(page, phone: string, code = FIXED_SMS_CODE) {
  await page.goto('/user/login')
  await page.locator('#login-phone').fill(phone)
  await page.locator('#login-send-code').click()
  await expect(page.getByText('验证码已发送')).toBeVisible()
  await page.locator('#login-code').fill(code)
  await agree(page)
  await page.locator('#login-submit').click()
}

test.describe('ACC · 账号与个人中心', () => {
  test('TC-001 手机号验证码注册登录', async ({ page }) => {
    const phone = randomPhone()
    await login(page, phone)

    await expect(page).toHaveURL(/\/user\/profile$/)
    await expect(page.locator('#profile-phone')).toHaveValue(phone)
    await expect(page.locator('#profile-nickname')).not.toHaveValue('')
  })

  test('TC-002 验证码错误时拒绝登录', async ({ page }) => {
    const phone = randomPhone()
    await page.goto('/user/login')
    await page.locator('#login-phone').fill(phone)
    await page.locator('#login-send-code').click()
    await expect(page.getByText('验证码已发送')).toBeVisible()
    await page.locator('#login-code').fill('000000')
    await agree(page)
    await page.locator('#login-submit').click()

    await expect(page.getByText('验证码错误')).toBeVisible()
    await expect(page).toHaveURL(/\/user\/login$/)
    expect(await page.evaluate(() => localStorage.getItem('token'))).toBeNull()
  })

  test('TC-003 修改个人资料后仍然生效', async ({ page }) => {
    const phone = randomPhone()
    await login(page, phone)
    await expect(page).toHaveURL(/\/user\/profile$/)

    const nickname = `昵称-${Date.now()}`
    await page.locator('#profile-nickname').fill(nickname)
    await page.locator('#profile-email').fill('qa@example.com')
    await page.locator('#profile-city').fill('310000')
    await page.locator('#profile-save').click()
    await expect(page.getByText('资料已保存')).toBeVisible()

    await page.reload()
    await expect(page.locator('#profile-nickname')).toHaveValue(nickname)
    await expect(page.locator('#profile-email')).toHaveValue('qa@example.com')
    await expect(page.locator('#profile-city')).toHaveValue('310000')
  })

  test('TC-004 未登录访问个人中心被拦截', async ({ page }) => {
    await page.goto('/user/profile')
    await expect(page).toHaveURL(/\/user\/login$/)
  })

  test('TC-005 收藏咨询师', async ({ page }) => {
    const phone = randomPhone()
    await login(page, phone)
    await expect(page).toHaveURL(/\/user\/profile$/)

    await page.locator('#favorite-consultant-id').fill(DISPLAYABLE_CONSULTANT_ID)
    await page.locator('#favorite-add').click()
    await expect(page.getByText('收藏成功')).toBeVisible()
    await expect(page.locator('#favorite-list .el-table__row')).toHaveCount(1)
    await expect(page.locator('#favorite-list .el-table__row').first()).toContainText(DISPLAYABLE_CONSULTANT_ID)

    // 幂等：重复收藏不报错，列表不重复
    await page.locator('#favorite-add').click()
    await expect(page.locator('#favorite-list .el-table__row')).toHaveCount(1)
  })

  test('TC-006 取消收藏（幂等）', async ({ page }) => {
    const phone = randomPhone()
    await login(page, phone)
    await expect(page).toHaveURL(/\/user\/profile$/)

    await page.locator('#favorite-consultant-id').fill(DISPLAYABLE_CONSULTANT_ID)
    await page.locator('#favorite-add').click()
    await expect(page.locator('#favorite-list .el-table__row')).toHaveCount(1)

    await page.locator('.favorite-remove').first().click()
    await page.getByRole('button', { name: '确定' }).click()
    await expect(page.getByText('已取消收藏')).toBeVisible()
    await expect(page.locator('#favorite-list .el-table__row')).toHaveCount(0)
  })

  test('TC-007 协议同意记录', async ({ page }) => {
    const phone = randomPhone()
    await login(page, phone)
    await expect(page).toHaveURL(/\/user\/profile$/)

    const agreements = page.locator('.el-card', { hasText: '协议同意记录' })
    await expect(agreements).toContainText('服务协议')
    await expect(agreements).toContainText('隐私政策')
    await expect(agreements).toContainText('v1')
  })

  test('TC-008 管理员禁用账号后旧会话失效', async ({ page, request }) => {
    const phone = randomPhone()
    await login(page, phone)
    await expect(page).toHaveURL(/\/user\/profile$/)

    const token = await page.evaluate(() => localStorage.getItem('token'))
    const me = await request.get('/api/v1/me', { headers: { Authorization: `Bearer ${token}` } })
    const accountId = (await me.json()).account.id

    const adminLogin = await request.post('/api/v1/auth/admin/login', {
      data: { phone: ADMIN_PHONE, password: ADMIN_PASSWORD },
    })
    expect(adminLogin.status()).toBe(200)
    const adminToken = (await adminLogin.json()).token

    const disabled = await request.post(`/api/v1/admin/accounts/${accountId}/disable`, {
      headers: { Authorization: `Bearer ${adminToken}` },
      data: { reason: 'QA 禁用' },
    })
    expect(disabled.status()).toBe(200)
    expect((await disabled.json()).status).toBe('DISABLED')

    await page.reload()
    await expect(page).toHaveURL(/\/user\/login$/)
    expect(await page.evaluate(() => localStorage.getItem('token'))).toBeNull()
  })

  test('TC-009 非管理员不得调用管理端接口', async ({ page, request }) => {
    const phone = randomPhone()
    await login(page, phone)
    await expect(page).toHaveURL(/\/user\/profile$/)

    const token = await page.evaluate(() => localStorage.getItem('token'))
    const me = await request.get('/api/v1/me', { headers: { Authorization: `Bearer ${token}` } })
    const accountId = (await me.json()).account.id

    const res = await request.post(`/api/v1/admin/accounts/${accountId}/disable`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { reason: '越权尝试' },
    })
    expect(res.status()).toBe(403)
  })
})
