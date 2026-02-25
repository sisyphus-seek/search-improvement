#!/usr/bin/env node
/**
 * 测试 rebrowser-playwright 反机器人检测能力
 */

import { chromium } from 'rebrowser-playwright';

async function testBotBypass() {
  console.log('启动 rebrowser-playwright 浏览器...');

  const browser = await chromium.launch({
    headless: true, // headless 模式
    channel: 'chrome',
    args: [
      '--disable-blink-features=AutomationControlled',
      '--disable-dev-shm-usage',
      '--no-sandbox',
      '--disable-gpu',
    ],
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',
  });

  // 关键：删除 navigator.webdriver 属性
  await context.addInitScript(() => {
    delete Object.getPrototypeOf(navigator).webdriver;

    // 额外的反检测措施
    Object.defineProperty(navigator, 'plugins', {
      get: () => [1, 2, 3, 4, 5],
    });

    Object.defineProperty(navigator, 'languages', {
      get: () => ['zh-CN', 'zh', 'en'],
    });

    // 伪装 chrome 对象
    window.chrome = {
      runtime: {},
    };
  });

  const page = await context.newPage();

  try {
    console.log('\n测试 1: bot.sannysoft.com 检测');
    await page.goto('https://bot.sannysoft.com', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000); // 等待页面完全加载

    // 检查结果
    const results = await page.evaluate(() => {
      const items = Array.from(document.querySelectorAll('.test-item'));
      return items.map(item => ({
        test: item.querySelector('strong')?.textContent || '',
        result: item.querySelector('.result')?.textContent || '',
      }));
    });

    console.log('\n检测结果:');
    let passed = 0;
    let failed = 0;
    for (const { test, result } of results) {
      const status = result.includes('passed') ? '✅ Pass' : '❌ Fail';
      if (result.includes('passed')) passed++;
      else failed++;
      console.log(`  ${status} - ${test}`);
    }
    console.log(`\n总计: ${passed} 通过, ${failed} 失败`);

    console.log('\n测试 2: Google 搜索');
    await page.goto('https://www.google.com', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);

    const hasCaptcha = await page.evaluate(() => {
      const captchaForm = document.querySelector('#captcha-form');
      return !!captchaForm;
    });

    if (hasCaptcha) {
      console.log('❌ Google 搜索触发 CAPTCHA');
    } else {
      console.log('✅ Google 搜索无 CAPTCHA');

      // 尝试搜索
      const searchInput = await page.$('textarea[name="q"]');
      if (searchInput) {
        await searchInput.fill('playwright bot bypass');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(2000);
        console.log('✅ 搜索成功执行');
      }
    }

    console.log('\n测试 3: 检测 WebDriver 属性');
    const webdriverStatus = await page.evaluate(() => {
      return {
        webdriver: navigator.webdriver,
        webdriverProto: Object.getPrototypeOf(navigator).webdriver,
        hasChrome: typeof window.chrome !== 'undefined',
        plugins: navigator.plugins.length,
        languages: navigator.languages,
      };
    });
    console.log('WebDriver 状态:');
    console.log(`  navigator.webdriver: ${webdriverStatus.webdriver}`);
    console.log(`  webdriver in prototype: ${webdriverStatus.webdriverProto}`);
    console.log(`  window.chrome: ${webdriverStatus.hasChrome}`);
    console.log(`  plugins: ${webdriverStatus.plugins}`);
    console.log(`  languages: ${webdriverStatus.languages.join(', ')}`);

  } catch (error) {
    console.error('测试出错:', error.message);
  } finally {
    await browser.close();
  }
}

testBotBypass().catch(console.error);
