import { test, expect } from '@playwright/test'

test.describe('Skeleton smoke (QA placeholder)', () => {
  test('homepage shell loads', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('h1')).toHaveText('咨询预约平台')
    await expect(page.getByText('工程骨架已就绪')).toBeVisible()
  })
})
