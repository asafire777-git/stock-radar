/**
 * 🔄 24/7 Smart Keep-Alive & Auto-Wakeup Script for Streamlit Cloud
 * Runs in headless Chromium via Playwright:
 * 1. Connects with real browser fingerprint & WebSocket session
 * 2. Checks if Streamlit is in 'Zzzz' sleeping state
 * 3. Automatically clicks 'Yes, get this app back up!' if sleeping
 * 4. Stays connected for 25s to register active session with Streamlit Cloud
 */

const { chromium } = require('playwright');

async function run() {
  console.log('====================================================');
  console.log('🚀 Starting Smart Browser Keep-Alive & Auto-Wakeup...');
  console.log('⏰ Timestamp:', new Date().toISOString());
  console.log('====================================================');

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 720 },
    locale: 'ko-KR',
  });

  const page = await context.newPage();

  try {
    const targetUrl = 'https://nstock-radar.streamlit.app/';
    console.log(`🌐 Navigating to ${targetUrl}...`);

    await page.goto(targetUrl, {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    });

    console.log('⏳ Page loaded. Waiting 5s for UI hydration...');
    await page.waitForTimeout(5000);

    // Check for sleeping state (Zzzz or Wakeup button)
    const wakeupButton = page.locator('button:has-text("Yes, get this app back up!")');
    const isSleeping = await wakeupButton.count() > 0 && await wakeupButton.first().isVisible();

    if (isSleeping) {
      console.log('⚠️ [SLEEP DETECTED] App is in sleep mode ("Zzzz")!');
      console.log('👉 Automatically clicking [Yes, get this app back up!] button...');
      await wakeupButton.first().click();
      console.log('⏳ Button clicked successfully! Waiting 35s for container to wake up...');
      await page.waitForTimeout(35000);
      console.log('✨ Wakeup sequence finished.');
    } else {
      console.log('✅ [ACTIVE] App is already awake! Maintaining WebSocket session for 20s...');
      await page.waitForTimeout(20000);
      console.log('✨ Active session registered with Streamlit Cloud.');
    }

    // Ping official domain as well
    console.log('🌐 Pinging https://nstock.kr/radar...');
    await page.goto('https://nstock.kr/radar', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);

    console.log('====================================================');
    console.log('🎉 Keep-Alive & Auto-Wakeup completed with 100% success!');
    console.log('====================================================');
  } catch (error) {
    console.error('❌ Error during keep-alive run:', error.message);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

run();
