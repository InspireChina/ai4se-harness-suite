import { defineConfig } from '@playwright/test'

// E2E 用例按归属分两层（详见 tests/README.md）：
//   tests/qa/  — QA 验收用例，合并闸门，用例基线在 docs/test-cases/e2e-cases/test-cases.md
//   tests/dev/ — 开发自测用例，仅供开发期快速反馈
export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  retries: 1,
  use: {
    baseURL: 'http://localhost:5173',
    viewport: { width: 1280, height: 800 },
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'qa', testDir: './tests/qa' },
    { name: 'dev', testDir: './tests/dev' },
  ],
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report' }],
  ],
})
