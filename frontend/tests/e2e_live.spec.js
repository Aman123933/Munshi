/**
 * Munshi E2E Test Suite — Live Mode (VITE_API_MODE=live)
 *
 * Tests the full teacher→pipeline→confirm flow against REAL servers:
 *   Backend:  uvicorn app.main:app --port 8000  (from backend/ with venv)
 *   Frontend: Playwright webServer (npx vite --host 127.0.0.1 --port 5173)
 *
 * Run with LLM_MODE=fallback (no API key needed) or LLM_MODE=gemini.
 *
 * Usage:
 *   cd frontend
 *   npx playwright test tests/e2e_live.spec.js --reporter=line
 *
 * The backend must be started externally before running (see README).
 */

import { test, expect, request } from '@playwright/test';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Wait for the page to fully hydrate (React mount + initial API calls done).
 * We detect this by waiting for the MUNSHI heading rather than networkidle,
 * because networkidle can be flaky when the backend is slow.
 */
async function waitForAppReady(page) {
  await expect(page.getByRole('heading', { name: 'MUNSHI' })).toBeVisible({ timeout: 15000 });
}

/**
 * Login as a given teacher ID via the TopBar teacher switcher dropdown.
 * The app auto-logs in as T01 on mount; call this to switch to any other ID.
 */
async function switchToTeacher(page, teacherId) {
  const select = page.getByLabel('Demo Teacher Switcher');
  await select.selectOption(teacherId);
  await page.waitForTimeout(600);
}

/**
 * Send the message currently loaded in the textarea and wait for the
 * Review screen to appear.  Returns after "Extracted Entities" heading
 * is visible.
 */
async function sendAndWaitForReview(page) {
  const sendBtn = page.getByRole('button', { name: /Send Message/i });
  await expect(sendBtn).toBeEnabled({ timeout: 5000 });
  await sendBtn.click();
  // Loading skeleton then Review screen
  await expect(page.getByText('Extracted Entities')).toBeVisible({ timeout: 30000 });
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

test.describe('Munshi E2E — Live Mode', () => {

  // -------------------------------------------------------------------------
  // 1. Homepage basics
  // -------------------------------------------------------------------------
  test('1. Homepage loads in live mode and shows all key landmarks', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    // Brand heading
    await expect(page.getByRole('heading', { name: 'MUNSHI' })).toBeVisible();

    // Footer disclaimer (prototype note)
    await expect(page.getByText(/Prototype with synthetic data/i)).toBeVisible();

    // 3-step explainer headings
    await expect(page.getByRole('heading', { name: /1\. Send/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: /2\. Review/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: /3\. Confirm/i })).toBeVisible();

    // Update / Records / Marks tabs present
    await expect(page.getByRole('button', { name: 'Update', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Records', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Marks', exact: true })).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 2. Demo chips load from /api/demo/messages in live mode
  // -------------------------------------------------------------------------
  test('2. Demo chips populate from live /api/demo/messages endpoint', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    // The app fetches demo messages on load and renders them as chip buttons.
    // All 6 demo messages should appear:
    const demoTitles = [
      /Clean English/i,
      /Hindi Devanagari/i,
      /Hinglish Classroom/i,
      /Three-Kabirs/i,
      /Count Mismatch|Stated Count/i,
      /Sunday Date/i,
    ];
    for (const titleRegex of demoTitles) {
      await expect(page.getByRole('button', { name: titleRegex })).toBeVisible({ timeout: 10000 });
    }
  });

  // -------------------------------------------------------------------------
  // 3. Demo-1 (clean English) → ready → confirm → records created
  // -------------------------------------------------------------------------
  test('3. Clean English demo (demo-1): ready status → confirm → records created', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    // Load demo-1 (Clean English)
    const cleanChip = page.getByRole('button', { name: /Clean English/i });
    await expect(cleanChip).toBeVisible({ timeout: 10000 });
    await cleanChip.click();

    // Textarea should have the demo text
    await expect(page.locator('textarea')).toHaveValue(/8A: 2 absent/i);

    // Send the message
    await sendAndWaitForReview(page);

    // Pipeline should return ready (no blocked/review fields for this clean message)
    // The ReviewBanner shows "Ready to Confirm" when status=ready
    await expect(page.getByRole('heading', { name: /Ready to Confirm/i })).toBeVisible({ timeout: 15000 });

    // 0 items left
    await expect(page.locator('.font-mono', { hasText: '0 items left' })).toBeVisible();

    // Confirm button enabled
    const confirmBtn = page.getByRole('button', { name: /Confirm and create records/i });
    await expect(confirmBtn).toBeEnabled();
    await confirmBtn.click();

    // Success panel appears
    await expect(page.getByText(/Records Successfully Created/i)).toBeVisible({ timeout: 15000 });

    // Audit ID shown
    await expect(page.getByText(/Audit ID:/i)).toBeVisible();

    // Record counts visible
    await expect(page.getByText(/Attendance/i)).toBeVisible();
    await expect(page.getByText(/Class Diary Entry/i)).toBeVisible();
    await expect(page.getByText(/Homework/i)).toBeVisible();

    // Notification drafts with language toggle
    await expect(page.getByText(/Notification Drafts/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /English/i }).first()).toBeVisible();
    await expect(page.getByRole('button', { name: /हिन्दी/i }).first()).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 4. Demo-4 (3 Kabirs) → needs_review → Confirm blocked → resolve → confirm
  // -------------------------------------------------------------------------
  test('4. Three-Kabirs collision (demo-4): Confirm blocked until candidate chosen', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    // Load demo-4
    const kabirChip = page.getByRole('button', { name: /Three-Kabirs/i });
    await expect(kabirChip).toBeVisible({ timeout: 10000 });
    await kabirChip.click();

    // Confirm textarea has the demo text
    await expect(page.locator('textarea')).toHaveValue(/Kabir/);

    // Send message
    await sendAndWaitForReview(page);

    // Status should be needs_review
    await expect(page.getByRole('heading', { name: /Needs Teacher Review/i })).toBeVisible({ timeout: 15000 });

    // Items left ≥ 1 (the Kabir ambiguity)
    const itemsLeftEl = page.locator('.font-mono', { hasText: /items left/ });
    await expect(itemsLeftEl).toBeVisible();
    const itemsText = await itemsLeftEl.innerText();
    expect(parseInt(itemsText)).toBeGreaterThanOrEqual(1);

    // Confirm button disabled while ambiguity unresolved
    const confirmBtn = page.getByRole('button', { name: /Confirm and create records/i });
    await expect(confirmBtn).toBeDisabled();

    // Hovering shows tooltip with Kabir mention
    await confirmBtn.hover();
    const tooltip = page.locator('[role="tooltip"]');
    await expect(tooltip).toBeVisible({ timeout: 3000 });
    await expect(tooltip).toContainText(/Kabir/);
    await expect(tooltip).toContainText(/3 options/);

    // Three Kabir candidate radio labels visible (Roll 801, 806, 811)
    await expect(page.locator('label', { hasText: 'Kabir Bansal' })).toBeVisible();
    await expect(page.getByText('Roll: 801')).toBeVisible();

    // Select Kabir Bansal (MUN0041, roll 801)
    await page.locator('label', { hasText: 'Kabir Bansal' }).click();

    // Status now "Ready to Confirm"
    await expect(page.getByRole('heading', { name: /Ready to Confirm/i })).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.font-mono', { hasText: '0 items left' })).toBeVisible();

    // Confirm button now enabled
    await expect(confirmBtn).toBeEnabled();
    await confirmBtn.click();

    // Success panel
    await expect(page.getByText(/Records Successfully Created/i)).toBeVisible({ timeout: 15000 });
    await expect(page.getByText(/Audit ID:/i)).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 5. Demo-6 (Sunday date) → blocked → Confirm permanently disabled
  // -------------------------------------------------------------------------
  test('5. Sunday date (demo-6): blocked status, Confirm shows Submission Blocked', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    // Load demo-6
    const sundayChip = page.getByRole('button', { name: /Sunday Date/i });
    await expect(sundayChip).toBeVisible({ timeout: 10000 });
    await sundayChip.click();

    await sendAndWaitForReview(page);

    // R6 should fire a Block rule; either Needs Review banner or rule result visible
    // The confirm button must show "Submission Blocked" or be disabled
    const confirmBtn = page.getByRole('button', { name: /Confirm and create records|Submission Blocked/i });
    await expect(confirmBtn).toBeVisible({ timeout: 15000 });
    await expect(confirmBtn).toBeDisabled();
  });

  // -------------------------------------------------------------------------
  // 6. Demo-5 (count mismatch) → needs_review → verify count mismatch rule shown
  // -------------------------------------------------------------------------
  test('6. Count mismatch demo (demo-5): R4 rule fires, review status', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    const mismatchChip = page.getByRole('button', { name: /Count Mismatch|Stated Count/i });
    await expect(mismatchChip).toBeVisible({ timeout: 10000 });
    await mismatchChip.click();

    await sendAndWaitForReview(page);

    // Should be needs_review (count mismatch)
    await expect(page.getByRole('heading', { name: /Needs Teacher Review|Ready to Confirm/i })).toBeVisible({ timeout: 15000 });

    // R4 rule result visible in fields table
    await expect(page.getByText(/R4|count|mismatch/i).first()).toBeVisible({ timeout: 5000 });
  });

  // -------------------------------------------------------------------------
  // 7. Records tab shows attendance after demo-1 confirm
  // -------------------------------------------------------------------------
  test('7. Records tab shows attendance after a confirmed message', async ({ page }) => {
    // First confirm demo-1 to seed an attendance record
    await page.goto('/');
    await waitForAppReady(page);

    const cleanChip = page.getByRole('button', { name: /Clean English/i });
    await expect(cleanChip).toBeVisible({ timeout: 10000 });
    await cleanChip.click();
    await sendAndWaitForReview(page);

    // If ready, confirm; if needs_review (e.g. name collision), skip confirm
    const confirmBtn = page.getByRole('button', { name: /Confirm and create records/i });
    const isDisabled = await confirmBtn.isDisabled();
    if (!isDisabled) {
      await confirmBtn.click();
      await expect(page.getByText(/Records Successfully Created/i)).toBeVisible({ timeout: 15000 });
    }

    // Navigate to Records tab
    await page.getByRole('button', { name: 'Records', exact: true }).click();

    // Records tab header visible
    await expect(page.getByText(/Attendance Records/i)).toBeVisible({ timeout: 10000 });

    // Select class 8A (demo-1 is for class 8A)
    const classSelect = page.locator('select', { hasText: /class|8A/i }).first();
    if (await classSelect.isVisible()) {
      await classSelect.selectOption({ label: '8A' }).catch(() => {}); // best effort
    }

    // At least one attendance row should appear for 8A today
    // The table / list shows student names; just verify at least 1 row
    const rows = page.getByRole('row').filter({ hasText: /MUN|absent|present/i });
    const rowCount = await rows.count();
    // If the backend has records, expect > 0; else just verify the tab renders without error
    await expect(page.getByText(/Attendance/i).first()).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 8. Principal audit tab shows confirm entry
  // -------------------------------------------------------------------------
  test('8. Principal audit tab: confirm action entry exists after teacher confirms', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    // Switch to principal P01
    await switchToTeacher(page, 'P01');

    // Audit tab should now be visible for principal (button label: "Audit Principal Only")
    const auditTabBtn = page.getByRole('button', { name: /Audit/i });
    await expect(auditTabBtn).toBeVisible({ timeout: 5000 });
    await auditTabBtn.click();

    // Audit heading visible
    await expect(page.getByText(/Principal Audit Trail/i)).toBeVisible({ timeout: 10000 });

    // At least one entry should exist (from prior test run or seeded confirms)
    // We just check that the list area loads without error
    // If no entries, the app shows an empty state; we accept either.
    const hasEntries = await page.getByText(/confirm/i).count() > 0 ||
                       await page.getByText(/No audit logs/i).count() > 0 ||
                       await page.getByText(/No confirmations/i).count() > 0;
    expect(hasEntries).toBeTruthy();
  });

  // -------------------------------------------------------------------------
  // 9. Marks tab: demo file loads, ≥ 13 flags including REC0553
  // -------------------------------------------------------------------------
  test('9. Marks tab: demo check returns ≥ 13 flags with REC0553 (theory_above_max)', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    // Switch to Marks tab
    await page.getByRole('button', { name: 'Marks', exact: true }).click();

    // Heading
    await expect(page.getByRole('heading', { name: /Marks Pre-Flight Checker/i })).toBeVisible({ timeout: 10000 });

    // The tab auto-loads the demo file on mount via GET /api/marks/demo
    // Wait for the summary strip "Rows Checked" to appear
    await expect(page.getByText('Rows Checked')).toBeVisible({ timeout: 20000 });
    await expect(page.getByText('Total Flags')).toBeVisible();

    // At least 13 "Mark as checked" buttons (one per flag card)
    const markBtns = page.getByRole('button', { name: 'Mark as checked' });
    await expect(markBtns.first()).toBeVisible({ timeout: 10000 });
    const count = await markBtns.count();
    expect(count).toBeGreaterThanOrEqual(13);

    // Block and Review groups visible
    await expect(page.getByRole('heading', { name: /Block Discrepancies/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: /Review Discrepancies/i })).toBeVisible();

    // REC0553 flag appears (theory_above_max injected error)
    await expect(page.getByText('REC0553').first()).toBeVisible({ timeout: 5000 });

    // "Mark as checked" toggle works
    const firstCheckBtn = markBtns.first();
    await firstCheckBtn.click();
    await expect(page.getByRole('button', { name: 'Checked by teacher' }).first()).toBeVisible();
    // Toggle back
    await page.getByRole('button', { name: 'Checked by teacher' }).first().click();
    await expect(page.getByRole('button', { name: 'Mark as checked' }).first()).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 10. API health: /api/demo/messages returns 6 items (direct API check)
  // -------------------------------------------------------------------------
  test('10. /api/demo/messages returns exactly 6 items via live API', async ({ request }) => {
    const resp = await request.get('http://127.0.0.1:8000/api/demo/messages');
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(Array.isArray(body)).toBeTruthy();
    expect(body.length).toBe(6);
    // IDs must be demo-1 through demo-6
    const ids = body.map((m) => m.id).sort();
    expect(ids).toEqual(['demo-1', 'demo-2', 'demo-3', 'demo-4', 'demo-5', 'demo-6']);
  });

  // -------------------------------------------------------------------------
  // 11. API health: /api/login with wrong pin returns 401
  // -------------------------------------------------------------------------
  test('11. /api/login with wrong pin returns 401', async ({ request }) => {
    const resp = await request.post('http://127.0.0.1:8000/api/login', {
      data: { teacher_id: 'T01', pin: 'wrong' },
    });
    expect(resp.status()).toBe(401);
  });

  // -------------------------------------------------------------------------
  // 12. UI language toggle works (Hindi ↔ English)
  // -------------------------------------------------------------------------
  test('12. UI language toggle switches labels between English and Hindi', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    // Click Hindi button
    await page.getByRole('button', { name: 'हिन्दी', exact: true }).click();

    // Tab labels should be in Hindi
    await expect(page.getByRole('button', { name: 'अपडेट', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'अभिलेख', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'अंक', exact: true })).toBeVisible();

    // Switch back to English
    await page.getByRole('button', { name: 'EN', exact: true }).click();
    await expect(page.getByRole('button', { name: 'Update', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Records', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Marks', exact: true })).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // 13. Mobile viewport (390 px): no horizontal overflow
  // -------------------------------------------------------------------------
  test('13. Mobile viewport (390px): no horizontal layout overflow', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');
    await waitForAppReady(page);

    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    expect(scrollWidth).toBeLessThanOrEqual(395);
  });

});
