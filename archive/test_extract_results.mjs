#!/usr/bin/env node
/**
 * 测试 Google 搜索结果提取
 */

import { chromium } from 'rebrowser-playwright';

const query = process.argv[2] || 'playwright bot bypass';

async function test() {
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

  await context.addInitScript(() => {
    delete Object.getPrototypeOf(navigator).webdriver;
    Object.defineProperty(navigator, 'plugins', {
      get: () => [1, 2, 3, 4, 5],
    });
    Object.defineProperty(navigator, 'languages', {
      get: () => ['zh-CN', 'zh', 'en'],
    });
    window.chrome = {
      runtime: {},
      loadTimes: function() {},
      csi: function() {},
      app: {},
    };
  });

  const page = await context.newPage();

  try {
    console.log(`\n搜索: ${query}\n`);

    await page.goto('https://www.google.com', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(1000);

    const searchInput = await page.$('textarea[name="q"]');
    if (!searchInput) {
      console.error('找不到搜索框');
      return;
    }

    await searchInput.fill(query);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(3000);

    // 截图保存页面内容
    const content = await page.content();

    // 提取搜索结果 - 尝试多种选择器
    console.log('尝试提取搜索结果...\n');

    const results = await page.evaluate(() => {
      const extracted = [];

      // 方法 1: 使用 div[data-hveid]
      const items1 = Array.from(document.querySelectorAll('div[data-hveid]'));
      if (items1.length > 0) {
        console.log('使用 div[data-hveid] 选择器');
        for (const item of items1) {
          const titleEl = item.querySelector('h3');
          const linkEl = item.querySelector('a[href]');
          const snippetEl = item.querySelector('div[data-sncf]');

          if (titleEl && linkEl) {
            extracted.push({
              title: titleEl.textContent.trim(),
              url: linkEl.href,
              snippet: snippetEl ? snippetEl.textContent.trim() : ''
            });
          }
        }
      }

      // 方法 2: 使用 .g (旧的 Google 搜索结果类)
      if (extracted.length === 0) {
        console.log('使用 .g 选择器');
        const items2 = Array.from(document.querySelectorAll('.g'));
        for (const item of items2) {
          const titleEl = item.querySelector('h3');
          const linkEl = item.querySelector('a');
          const snippetEl = item.querySelector('.st');

          if (titleEl && linkEl) {
            extracted.push({
              title: titleEl.textContent.trim(),
              url: linkEl.href,
              snippet: snippetEl ? snippetEl.textContent.trim() : ''
            });
          }
        }
      }

      // 方法 3: 使用所有 h3 和链接
      if (extracted.length === 0) {
        console.log('使用通用 h3 选择器');
        const titles = Array.from(document.querySelectorAll('h3'));
        for (const titleEl of titles) {
          const parentLink = titleEl.closest('a');
          if (parentLink) {
            const parentDiv = parentLink.closest('div');
            let snippet = '';
            if (parentDiv) {
              const texts = Array.from(parentDiv.querySelectorAll('span, div'))
                .map(el => el.textContent)
                .filter(t => t && t.length > 50);
              snippet = texts[0] || '';
            }
            extracted.push({
              title: titleEl.textContent.trim(),
              url: parentLink.href,
              snippet: snippet
            });
          }
        }
      }

      return extracted;
    });

    console.log(`提取到 ${results.length} 个结果:\n`);
    for (let i = 0; i < Math.min(results.length, 10); i++) {
      const r = results[i];
      console.log(`${i + 1}. ${r.title}`);
      console.log(`   ${r.url}`);
      if (r.snippet) {
        console.log(`   ${r.snippet.substring(0, 100)}...`);
      }
      console.log();
    }

    console.log(JSON.stringify(results, null, 2));

  } catch (error) {
    console.error('错误:', error.message);
  } finally {
    await browser.close();
  }
}

test().catch(console.error);
