import { test, expect } from '@playwright/test'

const BASE = 'http://localhost:5173'
const ADMIN_EMAIL = 'admin@test.com'
const ADMIN_PASSWORD = 'password'

/* ─────────────── Public Pages ─────────────── */

test.describe('Public Pages', () => {

  test('TC-001 首页加载', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('h1')).toHaveText('专业咨询服务')
    await expect(page.locator('text=免费注册')).toBeVisible()
    await expect(page.locator('text=立即预约')).toBeVisible()
    await expect(page.locator('text=© 2026 咨询预约平台')).toBeVisible()
  })

  test('TC-002 登录页渲染', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('h2')).toHaveText('登录')
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toHaveText('登录')
    await expect(page.locator('text=还没有账号？')).toBeVisible()
  })

  test('TC-003 注册页渲染', async ({ page }) => {
    await page.goto('/register')
    await expect(page.locator('h2')).toHaveText('注册')
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toHaveText('注册')
    await expect(page.locator('text=已有账号？')).toBeVisible()
  })

  test('TC-004 公开 API 可用', async ({ request }) => {
    let resp = await request.get(`${BASE}/api/v1/data-dictionaries`)
    expect(resp.status()).toBe(200)

    resp = await request.get(`${BASE}/api/v1/business-rules`)
    expect(resp.status()).toBe(200)

    resp = await request.get(`${BASE}/api/v1/consultants`)
    expect(resp.status()).toBe(200)
    const body = await resp.json()
    expect(body.length).toBeGreaterThanOrEqual(3)
  })

  test('TC-005 导航跳转', async ({ page }) => {
    await page.goto('/')
    await page.click('text=登录')
    await expect(page).toHaveURL('/login')

    await page.click('text=立即注册')
    await expect(page).toHaveURL('/register')
  })
})

/* ─────────────── Auth & User Lifecycle (serial: share registered email) ─────────────── */

let registerEmail = ''

test.describe.serial('Auth & User Lifecycle', () => {

  test('TC-006 管理员登录成功', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', ADMIN_EMAIL)
    await page.fill('input[type="password"]', ADMIN_PASSWORD)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 })
    await expect(page.locator('h1')).toHaveText('管理仪表盘')
  })

  test('TC-007 错误密码提示', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', ADMIN_EMAIL)
    await page.fill('input[type="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')
    await expect(page.locator('.error')).toBeVisible({ timeout: 8000 })
  })

  test('TC-008 注册新用户', async ({ page }) => {
    registerEmail = `e2e_${Date.now()}@test.com`
    await page.goto('/register')

    await page.locator('input[placeholder*="姓名"]').fill('E2E用户')
    await page.fill('input[type="email"]', registerEmail)
    await page.locator('input[placeholder*="选填"]').fill('13800000001')
    await page.fill('input[type="password"]', 'Test123456')

    await page.click('button[type="submit"]')
    await page.waitForURL('**/user/dashboard', { timeout: 10000 })
    await expect(page.locator('text=E2E用户')).toBeVisible()
  })

  test('TC-009 重复邮箱注册', async ({ page }) => {
    await page.goto('/register')
    await page.locator('input[placeholder*="姓名"]').fill('重复用户')
    await page.fill('input[type="email"]', registerEmail)
    await page.fill('input[type="password"]', 'Test123456')
    await page.click('button[type="submit"]')
    await expect(page.locator('.error')).toBeVisible({ timeout: 8000 })
  })

  test('TC-010 新用户登录', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', registerEmail)
    await page.fill('input[type="password"]', 'Test123456')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/user/dashboard', { timeout: 10000 })
    await expect(page.locator('h1').first()).toHaveText('用户中心')
  })

  test('TC-011 用户仪表盘', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', registerEmail)
    await page.fill('input[type="password"]', 'Test123456')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/user/dashboard', { timeout: 10000 })

    await expect(page.locator('.stat-card').filter({ hasText: '总预约' })).toBeVisible()
    await expect(page.locator('text=待确认')).toBeVisible()
    await expect(page.locator('text=已完成')).toBeVisible()
  })

  test('TC-012 浏览咨询师', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', registerEmail)
    await page.fill('input[type="password"]', 'Test123456')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/user/dashboard', { timeout: 10000 })

    await page.goto('/user/book')
    await expect(page.locator('h1')).toHaveText('预约咨询')
    await expect(page.locator('text=张医生')).toBeVisible()
    await expect(page.locator('text=李律师')).toBeVisible()
    await expect(page.locator('text=王教练')).toBeVisible()
  })

  test('TC-013 预约 + 取消', async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.fill('input[type="email"]', registerEmail)
    await page.fill('input[type="password"]', 'Test123456')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/user/dashboard', { timeout: 10000 })

    // Go to book page
    await page.goto('/user/book')
    await expect(page.locator('h1')).toHaveText('预约咨询')

    // Step 1: Select consultant
    await page.locator('text=张医生').click()
    await expect(page.locator('text=2. 选择日期')).toBeVisible()

    // Step 2: Pick a date
    const dateBtn = page.locator('div.date-list button').first()
    await expect(dateBtn).toBeVisible()
    await dateBtn.click()
    await page.waitForTimeout(1500)

    // Step 3: Pick a time slot
    const slotBtn = page.locator('div.slot-list button').first()
    if (await slotBtn.isVisible({ timeout: 5000 })) {
      await slotBtn.click()
      await expect(page.locator('text=4. 备注')).toBeVisible()

      // Step 4: Add note and submit
      await page.fill('textarea', 'E2E booking test')
      await page.click('text=确认预约')
      await page.waitForURL('**/user/appointments', { timeout: 10000 })

      // Verify appointment created
      await expect(page.locator('h1')).toHaveText('我的预约')

      // Cancel the appointment
      const cancelBtn = page.locator('button:has-text("取消")').first()
      if (await cancelBtn.isVisible({ timeout: 5000 })) {
        page.once('dialog', dialog => dialog.accept())
        await cancelBtn.click()
        await page.waitForTimeout(1500)
        await expect(page.locator('.status.cancelled').first()).toBeVisible({ timeout: 5000 })
      }
    }
  })

  test('TC-014 编辑个人信息', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', registerEmail)
    await page.fill('input[type="password"]', 'Test123456')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/user/dashboard', { timeout: 10000 })

    await page.goto('/user/profile')
    const nameInput = page.locator('input').nth(1)
    await nameInput.fill('E2E用户-已改名')
    const [dialog] = await Promise.all([
      page.waitForEvent('dialog', { timeout: 5000 }),
      page.click('text=保存'),
    ])
    expect(dialog.message()).toContain('保存成功')
    await dialog.dismiss()
  })
})

/* ─────────────── Admin Flows (independent tests) ─────────────── */

test.describe('Admin Flows', () => {

  test('TC-015 仪表盘统计', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', ADMIN_EMAIL)
    await page.fill('input[type="password"]', ADMIN_PASSWORD)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 })

    await expect(page.locator('h1')).toHaveText('管理仪表盘')
    await expect(page.locator('.stat-card').filter({ hasText: '用户数' })).toBeVisible()
    await expect(page.locator('.stat-card').filter({ hasText: '咨询师' })).toBeVisible()
    await expect(page.locator('.stat-card').filter({ hasText: '总预约' })).toBeVisible()
    await expect(page.locator('.stat-card').filter({ hasText: '待确认' })).toBeVisible()
    await expect(page.locator('.stat-card').filter({ hasText: '网点' })).toBeVisible()
  })

  test('TC-016 用户管理', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', ADMIN_EMAIL)
    await page.fill('input[type="password"]', ADMIN_PASSWORD)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 })

    await page.goto('/admin/users')
    await expect(page.locator('table')).toBeVisible({ timeout: 10000 })
    await expect(page.locator('text=admin@test.com')).toBeVisible()
    await expect(page.locator('text=管理员')).toBeVisible()

    const toggleBtn = page.locator('button:has-text("禁用"), button:has-text("启用")').first()
    if (await toggleBtn.isVisible()) {
      await toggleBtn.click()
      await page.waitForTimeout(1000)
    }
  })

  test('TC-017 咨询师管理', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', ADMIN_EMAIL)
    await page.fill('input[type="password"]', ADMIN_PASSWORD)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 })

    await page.locator('a:has-text("咨询师管理")').click()
    await page.waitForURL('**/admin/consultants', { timeout: 10000 })
    await expect(page.locator('table')).toBeVisible({ timeout: 10000 })
    await expect(page.locator('text=张医生')).toBeVisible()
    await expect(page.locator('text=李律师')).toBeVisible()
    await expect(page.locator('text=王教练')).toBeVisible()
  })

  test('TC-018 预约管理', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', ADMIN_EMAIL)
    await page.fill('input[type="password"]', ADMIN_PASSWORD)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 })

    await page.locator('a:has-text("预约管理")').click()
    await page.waitForURL('**/admin/appointments', { timeout: 10000 })
    await expect(page.locator('h1')).toHaveText('预约管理')
  })

  test('TC-019 网点 CRUD', async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.fill('input[type="email"]', ADMIN_EMAIL)
    await page.fill('input[type="password"]', ADMIN_PASSWORD)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 })

    // Go to branches
    await page.locator('a:has-text("网点管理")').click()
    await page.waitForURL('**/admin/branches', { timeout: 10000 })
    await expect(page.locator('h1')).toHaveText('网点管理')
    await expect(page.locator('text=朝阳咨询中心')).toBeVisible({ timeout: 10000 })
    await expect(page.locator('text=海淀咨询中心')).toBeVisible()
    await expect(page.locator('text=浦东咨询中心')).toBeVisible()

    // ── CREATE ──
    await page.click('text=新增网点')
    await expect(page.locator('.modal')).toBeVisible()

    // Modal: <div class="form-group"><label>名称</label><input v-model="form.name" class="input" /></div>
    await page.locator('.modal .form-group').nth(0).locator('input').fill('E2E测试网点')
    await page.locator('.modal .form-group').nth(1).locator('input').fill('东城区测试大街1号')
    await page.locator('.modal .form-group').nth(2).locator('input').fill('010-88889999')
    await page.locator('.modal button:has-text("保存")').click()
    await page.waitForTimeout(1500)
    await expect(page.locator('text=E2E测试网点')).toBeVisible({ timeout: 5000 })

    // ── EDIT ──
    await page.locator('tr:has-text("E2E测试网点") button:has-text("编辑")').click()
    await expect(page.locator('.modal')).toBeVisible()
    await page.locator('.modal .form-group').nth(0).locator('input').fill('E2E测试网点-已改')
    await page.locator('.modal button:has-text("保存")').click()
    await page.waitForTimeout(1500)
    await expect(page.locator('text=E2E测试网点-已改')).toBeVisible({ timeout: 5000 })

    // ── DELETE ──
    page.once('dialog', dialog => dialog.accept())
    await page.locator('tr:has-text("E2E测试网点-已改") button:has-text("删除")').click()
    await page.waitForTimeout(1500)
    await expect(page.locator('text=E2E测试网点-已改')).toHaveCount(0, { timeout: 5000 })
  })
})

/* ─────────────── Edge Cases ─────────────── */

test.describe('Edge Cases', () => {

  test('TC-020 未登录访问管理页', async ({ page }) => {
    await page.goto('/')
    await page.evaluate(() => localStorage.clear())
    await page.goto('/admin/dashboard')
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 })
  })

  test('TC-021 未登录访问用户页', async ({ page }) => {
    await page.goto('/')
    await page.evaluate(() => localStorage.clear())
    await page.goto('/user/dashboard')
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 })
  })

  test('TC-022 首页 CTA 可见', async ({ page }) => {
    await page.goto('/')
    await page.evaluate(() => localStorage.clear())
    await page.goto('/')
    const cta = page.locator('text=免费注册')
    await expect(cta).toBeVisible()
  })
})
