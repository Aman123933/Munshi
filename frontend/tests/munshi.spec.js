import { test, expect } from '@playwright/test';

test.describe('Munshi Frontend E2E Tests (Mock Mode)', () => {

  test('1. First-run explainer, demo chip selection, and sending message to review', async ({ page }) => {
    await page.goto('/');

    // Verify page title and brand heading
    await expect(page).toHaveTitle(/MUNSHI/i);
    await expect(page.getByRole('heading', { name: 'MUNSHI' })).toBeVisible();
    await expect(page.getByText('AI proposes. Rules verify. The teacher confirms.').first()).toBeVisible();

    // Verify 3-step explainer is present
    await expect(page.getByRole('heading', { name: '1. Send' })).toBeVisible();
    await expect(page.getByRole('heading', { name: '2. Review' })).toBeVisible();
    await expect(page.getByRole('heading', { name: '3. Confirm' })).toBeVisible();

    // Verify footer disclaimer
    await expect(page.getByText('Prototype with synthetic data. No real student data.')).toBeVisible();

    // Click demo chip for Kabir collision
    const loadDemoBtn = page.getByRole('button', { name: /Load: "8A: 3 absent — Kabir, Ayaan, Riya/i });
    await expect(loadDemoBtn).toBeVisible();
    await loadDemoBtn.click();

    // Check textarea contains the demo text
    const textarea = page.locator('textarea');
    await expect(textarea).toHaveValue(/8A: 3 absent — Kabir, Ayaan, Riya/);

    // Click Send Message button
    const sendButton = page.getByRole('button', { name: /Send Message/i });
    await expect(sendButton).toBeEnabled();
    await sendButton.click();

    // Expect navigation to Review screen
    await expect(page.getByText('Extracted Entities & Rule Verifications')).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('heading', { name: /Needs Teacher Review/i })).toBeVisible();
  });

  test('2. Review screen blocks Confirm until Kabir choice is made, then successfully creates records', async ({ page }) => {
    await page.goto('/');

    // Load demo message with 3-Kabirs collision
    await page.getByRole('button', { name: /Load: "8A: 3 absent — Kabir, Ayaan, Riya/i }).click();
    await page.getByRole('button', { name: /Send Message/i }).click();

    // Wait for review screen
    await expect(page.getByText('Extracted Entities & Rule Verifications')).toBeVisible({ timeout: 10000 });

    // Banner indicates review needed
    await expect(page.getByRole('heading', { name: /Needs Teacher Review/i })).toBeVisible();
    await expect(page.locator('.font-mono', { hasText: '1 items left' })).toBeVisible();

    // Confirm button must be disabled
    const disabledConfirmBtn = page.getByRole('button', { name: /Confirm and create records \(1/i });
    await expect(disabledConfirmBtn).toBeDisabled();

    // Verify tooltip shows ambiguity reason when hovered/focused
    await disabledConfirmBtn.hover();
    await expect(page.locator('role=tooltip')).toBeVisible();
    await expect(page.locator('role=tooltip')).toContainText(/Kabir/);
    await expect(page.locator('role=tooltip')).toContainText(/3 options/);

    // Radio candidate list for Kabir (Roll 801, 806, 811) must be present
    const kabirOption = page.locator('label', { hasText: 'Kabir Bansal' });
    await expect(kabirOption).toBeVisible();
    await expect(page.getByText('Roll: 801')).toBeVisible();

    // Select candidate: Kabir Bansal
    await kabirOption.click();

    // Banner should transition to READY TO CONFIRM with 0 items left
    await expect(page.getByRole('heading', { name: /Ready to Confirm/i })).toBeVisible();
    await expect(page.locator('.font-mono', { hasText: '0 items left' })).toBeVisible();

    // Confirm button must now be enabled
    const readyConfirmBtn = page.getByRole('button', { name: 'Confirm and create records', exact: true });
    await expect(readyConfirmBtn).toBeEnabled();

    // Click confirm to commit transaction
    await readyConfirmBtn.click();

    // Success panel must appear
    await expect(page.getByText(/Records Successfully Created/i)).toBeVisible({ timeout: 10000 });

    // Verify audit id is displayed
    await expect(page.getByText(/Audit ID:/i)).toBeVisible();

    // Verify created records: Attendance, Diary, Homework
    await expect(page.getByText(/Attendance Records/i)).toBeVisible();
    await expect(page.getByText(/Class Diary Entry/i)).toBeVisible();
    await expect(page.getByText(/Homework Task/i)).toBeVisible();

    // Verify notification drafts with language toggle and copy buttons
    await expect(page.getByText(/Notification Drafts/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /English/i }).first()).toBeVisible();
    await expect(page.getByRole('button', { name: /हिन्दी/i }).first()).toBeVisible();
    await expect(page.getByRole('button', { name: /Copy Draft/i }).first()).toBeVisible();
  });

  test('3. Marks tab displays summary strip and at least 13 flag cards with local check toggle', async ({ page }) => {
    await page.goto('/');

    // Switch to Marks tab
    const marksTabButton = page.getByRole('button', { name: 'Marks' });
    await marksTabButton.click();

    // Verify Marks Pre-Flight Checker header
    await expect(page.getByRole('heading', { name: /Marks Pre-Flight Checker/i })).toBeVisible();

    // Summary strip shows 703 rows checked
    await expect(page.getByText('703')).toBeVisible();
    await expect(page.getByText('Rows Checked')).toBeVisible();
    await expect(page.getByText('Total Flags')).toBeVisible();

    // Verify both Block and Review groups are present
    await expect(page.getByRole('heading', { name: /Block Discrepancies/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: /Review Discrepancies/i })).toBeVisible();

    // Check that at least 13 flag cards are displayed
    const markButtons = page.getByRole('button', { name: 'Mark as checked' });
    const count = await markButtons.count();
    expect(count).toBeGreaterThanOrEqual(13);

    // Test local "Mark as checked" toggle on the first card
    const firstCheckBtn = markButtons.first();
    await firstCheckBtn.click();
    await expect(page.getByRole('button', { name: 'Checked by teacher' }).first()).toBeVisible();

    // Click again to toggle back
    await page.getByRole('button', { name: 'Checked by teacher' }).first().click();
    await expect(page.getByRole('button', { name: 'Mark as checked' }).first()).toBeVisible();
  });

  test('4. UI language toggle switches labels between English and Hindi', async ({ page }) => {
    await page.goto('/');

    // Click Hindi switch
    const hindiButton = page.getByRole('button', { name: 'हिन्दी', exact: true });
    await hindiButton.click();

    // Verify tab labels in Hindi
    await expect(page.getByRole('button', { name: 'अपडेट', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'अभिलेख', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'अंक', exact: true })).toBeVisible();

    // Verify first-run explainer in Hindi
    await expect(page.getByText('AI प्रस्तावित करता है। नियम सत्यापन करते हैं। शिक्षक पुष्टि करते हैं।').first()).toBeVisible();
    await expect(page.getByRole('heading', { name: /1\. भेजें/i })).toBeVisible();

    // Switch back to English
    const enButton = page.getByRole('button', { name: 'EN', exact: true });
    await enButton.click();

    // Verify tab labels in English
    await expect(page.getByRole('button', { name: 'Update', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Records', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Marks', exact: true })).toBeVisible();
  });

  test('5. Usable at 390px mobile viewport without layout overflow', async ({ page }) => {
    // 390px width mobile viewport
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');

    // Verify top bar brand heading is visible
    await expect(page.getByRole('heading', { name: 'MUNSHI' })).toBeVisible();

    // Ensure horizontal scroll width does not exceed viewport width
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    expect(scrollWidth).toBeLessThanOrEqual(395); // minor tolerance for browser scrollbars
  });

});
