#!/usr/bin/env node
/**
 * 调试搜索结果提取
 */

import { chromium } from 'playwright';

const ANTI_DETECTION_SCRIPT = `
  Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
  });
  Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5],
  });
  Object.defineProperty(navigator, 'languages', {
    get: () => ['zh-CN', 'zh', 'en-US', 'en'],
  });
  window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {},
  };
`;

async function debugDuckDuckGo() {
  console.log('\n=== Debug DuckDuckGo ===');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  await page.addInitScript(ANTI_DETECTION_SCRIPT);

  const url = 'https://duckduckgo.com/html/?q=playwright+bot+bypass';
  console.log(`Navigating to: ${url}`);

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(2000);

  // 检查页面标题
  const title = await page.title();
  console.log(`Page title: ${title}`);

  // 检查当前 URL（可能有重定向）
  const currentUrl = page.url();
  console.log(`Current URL: ${currentUrl}`);

  // 检查是否有 result__a 链接
  const resultLinks = await page.$$eval('a.result__a', (elements) => {
    return elements.map((el) => ({
      text: el.textContent?.trim(),
      href: el.href,
    })).slice(0, 5);
  });

  console.log(`Found ${resultLinks.length} result__a links:`);
  for (const link of resultLinks) {
    console.log(`  - ${link.text}`);
    console.log(`    ${link.href}`);
  }

  // 尝试其他选择器
  console.log('\nTrying other selectors...');

  // 检查是否有 .result 类
  const resultDivs = await page.$$eval('.result', (elements) => {
    return elements.map((el) => ({
      class: el.className,
      html: el.innerHTML.substring(0, 200),
    })).slice(0, 3);
  });

  console.log(`Found ${resultDivs.length} .result divs:`);
  for (const div of resultDivs) {
    console.log(`  - class: ${div.class}`);
    console.log(`    html: ${div.html}...`);
  }

  // 截图
  await page.screenshot({ path: '/tmp/duckduckgo_debug.png' });
  console.log('\nScreenshot saved to /tmp/duckduckgo_debug.png');

  // 保存 HTML
  const html = await page.content();
  await (await import('fs')).writeFile('/tmp/duckduckgo_debug.html', html);
  console.log('HTML saved to /tmp/duckduckgo_debug.html');

  await browser.close();
}

async function debugBing() {
  console.log('\n=== Debug Bing ===');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  await page.addInitScript(ANTI_DETECTION_SCRIPT);

  const url = 'https://www.bing.com/search?q=AI+agents';
  console.log(`Navigating to: ${url}`);

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(2000);

  // 检查页面标题
  const title = await page.title();
  console.log(`Page title: ${title}`);

  // 检查当前 URL
  const currentUrl = page.url();
  console.log(`Current URL: ${currentUrl}`);

  // 检查是否有 b_algo 结果
  const results = await page.$$eval('li.b_algo', (items) => {
    const extracted = [];
    items.forEach((item) => {
      const link = item.querySelector('h2 a');
      if (link) {
        extracted.push({
          title: link.textContent?.trim(),
          href: link.href,
        });
      }
    });
    return extracted.slice(0, 5);
  });

  console.log(`Found ${results.length} b_algo results:`);
  for (const r of results) {
    console.log(`  - ${r.title}`);
    console.log(`    ${r.href}`);
  }

  // 截图
  await page.screenshot({ path: '/tmp/bing_debug.png' });
  console.log('\nScreenshot saved to /tmp/bing_debug.png');

  await browser.close();
}

async function main() {
  await debugDuckDuckGo();
  await debugBing();
}

main().catch(console.error);
