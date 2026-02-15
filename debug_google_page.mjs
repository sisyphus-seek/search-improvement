#!/usr/bin/env node
/**
 * 调试：保存 Google 搜索页面的 HTML
 */

import { chromium } from 'rebrowser-playwright';
import fs from 'fs';

const query = process.argv[2] || 'AI agents';

async function debug() {
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

    // 保存页面 HTML
    const html = await page.content();
    const outputFile = '/workspace/projects/search-improvement/debug_google_page.html';
    fs.writeFileSync(outputFile, html, 'utf8');

    console.log(`页面 HTML 已保存到: ${outputFile}`);
    console.log(`HTML 长度: ${html.length} 字符`);

    // 检查一些基本的页面元素
    const stats = await page.evaluate(() => {
      return {
        h3Count: document.querySelectorAll('h3').length,
        linkCount: document.querySelectorAll('a').length,
        dataHveidCount: document.querySelectorAll('[data-hveid]').length,
        gClassCount: document.querySelectorAll('.g').length,
        title: document.title,
      };
    });

    console.log('\n页面统计:');
    console.log(`  h3 标签数: ${stats.h3Count}`);
    console.log(`  链接数: ${stats.linkCount}`);
    console.log(`  data-hveid 元素数: ${stats.dataHveidCount}`);
    console.log(`  .g 类元素数: ${stats.gClassCount}`);
    console.log(`  页面标题: ${stats.title}`);

    // 尝试查看前 5 个 h3 标签
    const h3Texts = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('h3'))
        .slice(0, 5)
        .map(h3 => h3.textContent.trim());
    });

    console.log('\n前 5 个 h3 标签内容:');
    h3Texts.forEach((text, i) => {
      console.log(`  ${i + 1}. ${text}`);
    });

  } catch (error) {
    console.error('错误:', error.message);
    console.error(error.stack);
  } finally {
    await browser.close();
  }
}

debug().catch(console.error);
