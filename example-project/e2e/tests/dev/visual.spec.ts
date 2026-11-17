import { test, expect } from '@playwright/test'

test.describe('Dev visual smoke', () => {
  test('homepage shell visible', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('h1')).toBeVisible()
  })
})
