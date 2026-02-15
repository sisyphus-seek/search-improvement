#!/usr/bin/env node
/**
 * 简单测试 rebrowser-playwright 是否能绕过 Google CAPTCHA
 */

import { chromium } from 'rebrowser-playwright';

async function testGoogleSearch() {
  console.log('启动 rebrowser-playwright 浏览器...');

  const browser = await chromium.launch({
    headless: true,
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

  // 关键反检测措施
  await context.addInitScript(() => {
    // 删除 navigator.webdriver
    delete Object.getPrototypeOf(navigator).webdriver;

    // 伪装 plugins
    Object.defineProperty(navigator, 'plugins', {
      get: () => [1, 2, 3, 4, 5],
    });

    // 伪装 languages
    Object.defineProperty(navigator, 'languages', {
      get: () => ['zh-CN', 'zh', 'en'],
    });

    // 伪装 chrome 对象
    window.chrome = {
      runtime: {},
      loadTimes: function() {},
      csi: function() {},
      app: {},
    };
  });

  const page = await context.newPage();

  try {
    console.log('\n访问 Google...');
    await page.goto('https://www.google.com', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);

    // 检查是否有 CAPTCHA
    const hasCaptcha = await page.evaluate(() => {
      const captchaForm = document.querySelector('#captcha-form');
      const titleText = document.title;
      return {
        hasCaptchaForm: !!captchaForm,
        title: titleText,
      };
    });

    console.log('\n页面标题:', hasCaptcha.title);

    if (hasCaptcha.hasCaptchaForm) {
      console.log('❌ Google 触发了 CAPTCHA');
    } else {
      console.log('✅ Google 无 CAPTCHA');

      // 检查 WebDriver 属性
      const webdriverStatus = await page.evaluate(() => {
        return {
          webdriver: navigator.webdriver,
          webdriverProto: Object.getPrototypeOf(navigator).webdriver,
          hasChrome: typeof window.chrome !== 'undefined',
          userAgent: navigator.userAgent.substring(0, 60),
        };
      });
      console.log('\n反检测状态:');
      console.log(`  navigator.webdriver: ${webdriverStatus.webdriver}`);
      console.log(`  webdriver in prototype: ${webdriverStatus.webdriverProto}`);
      console.log(`  window.chrome: ${webdriverStatus.hasChrome}`);
      console.log(`  user agent: ${webdriverStatus.userAgent}...`);

      // 尝试搜索
      console.log('\n尝试搜索...');
      const searchInput = await page.$('textarea[name="q"]');
      if (searchInput) {
        await searchInput.fill('playwright bot bypass');
        await page.keyboard.press('Enter');

        // 等待搜索结果加载
        await page.waitForTimeout(3000);

        const resultCount = await page.evaluate(() => {
          const stats = document.querySelector('#result-stats');
          return stats ? stats.textContent : 'No stats';
        });

        console.log(`✅ 搜索成功！结果: ${resultCount}`);
      } else {
        console.log('❌ 找不到搜索框');
      }
    }

  } catch (error) {
    console.error('测试出错:', error.message);
  } finally {
    await browser.close();
    console.log('\n浏览器已关闭');
  }
}

testGoogleSearch().catch(console.error);
