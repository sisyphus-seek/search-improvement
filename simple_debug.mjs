#!/usr/bin/env node
/**
 * 简单调试：查看页面内容
 */

import { chromium } from 'playwright';

const ANTI_DETECTION_SCRIPT = `
  Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
  Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
  window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };
`;

async function debug() {
  console.log('=== Debug: DuckDuckGo ===');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  await page.addInitScript(ANTI_DETECTION_SCRIPT);

  const url = 'https://duckduckgo.com/html/?q=test';
  console.log(`Navigating to: ${url}`);

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);

    const title = await page.title();
    const currentUrl = page.url();

    console.log(`Title: ${title}`);
    console.log(`URL: ${currentUrl}`);

    // 获取所有链接
    const allLinks = await page.$$eval('a', (links) => {
      return links.map(l => ({
        text: l.textContent?.trim().substring(0, 50),
        href: l.href,
        class: l.className,
      })).filter(l => l.href && !l.href.startsWith('#')).slice(0, 20);
    });

    console.log(`\nFound ${allLinks.length} links (first 20):`);
    for (const link of allLinks) {
      console.log(`  [${link.class}] ${link.text}`);
      console.log(`    ${link.href}`);
    }

  } catch (e) {
    console.error(`Error: ${e.message}`);
  }

  await browser.close();
}

debug().catch(console.error);
