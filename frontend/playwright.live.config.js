/**
 * Playwright config for LIVE mode E2E tests (e2e_live.spec.js).
 *
 * Requires both servers to be running externally before this config is used:
 *   Backend:  cd backend && .venv/Scripts/python -m uvicorn app.main:app --port 8000
 *   Frontend: cd frontend && npx vite --host 127.0.0.1 --port 5173
 *
 * Usage:
 *   cd frontend
 *   npx playwright test tests/e2e_live.spec.js --config=playwright.live.config.js
 *   # or with LLM_MODE=fallback set in the backend environment
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: 'e2e_live.spec.js',
  fullyParallel: false,
  retries: 1,          // one retry on flaky network responses
  workers: 1,
  reporter: 'line',
  timeout: 60000,      // 60 s per test (LLM calls can be slow)
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'retain-on-failure',
    viewport: { width: 1280, height: 720 },
    // Extra time for live API calls
    actionTimeout: 20000,
    navigationTimeout: 30000,
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
      },
    },
  ],
  // webServer block intentionally omitted: both servers must be started externally.
  // This prevents Playwright from killing the backend when the test suite finishes.
});
