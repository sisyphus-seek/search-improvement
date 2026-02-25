#!/usr/bin/env node
/**
 * 统一浏览器搜索脚本 - 支持多个搜索引擎
 * 基于 rebrowser-playwright 绕过机器人检测
 */

import { chromium } from 'rebrowser-playwright';

const QUERY = process.argv[2];
const ENGINE = process.argv[3] || 'google';
const LIMIT = parseInt(process.argv[4]) || 10;

async function search(query, engine, limit) {
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

  // 反检测脚本
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
    Object.defineProperty(navigator, 'permissions', {
      get: () => ({
        query: () => Promise.resolve({ state: 'prompt' }),
      }),
    });
  });

  const page = await context.newPage();

  try {
    let url, searchBoxSelector, searchButtonSelector, resultsSelector;

    if (engine === 'google') {
      url = 'https://www.google.com';
      searchBoxSelector = 'textarea[name="q"]';
      searchButtonSelector = null;
      resultsSelector = 'h3';
    } else if (engine === 'bing') {
      url = 'https://www.bing.com';
      searchBoxSelector = 'input[name="q"]';
      searchButtonSelector = 'input[type="submit"]';
      resultsSelector = 'li.b_algo h2';
    } else if (engine === 'duckduckgo') {
      url = 'https://duckduckgo.com';
      searchBoxSelector = 'input[name="q"]';
      searchButtonSelector = 'input[type="submit"]';
      resultsSelector = 'a.result__a';
    } else if (engine === 'baidu') {
      url = 'https://www.baidu.com';
      searchBoxSelector = 'input[name="wd"]';
      searchButtonSelector = 'input[type="submit"]';
      resultsSelector = 'h3 a';
    } else {
      throw new Error(`Unknown engine: ${engine}`);
    }

    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(1500);

    const hasCaptcha = await page.evaluate(() => {
      const captcha = document.querySelector('#captcha-form') ||
                      document.querySelector('.g-recaptcha') ||
                      document.querySelector('[id*="captcha"]');
      return !!captcha;
    });

    if (hasCaptcha) {
      throw new Error('CAPTCHA detected');
    }

    const searchBox = await page.$(searchBoxSelector);
    if (!searchBox) {
      throw new Error('Search box not found');
    }

    await searchBox.type(query, { delay: 50 });
    await page.waitForTimeout(500);

    if (searchButtonSelector) {
      const button = await page.$(searchButtonSelector);
      if (button) {
        await button.click();
      } else {
        await page.keyboard.press('Enter');
      }
    } else {
      await page.keyboard.press('Enter');
    }

    await page.waitForTimeout(3000);

    // 保存页面 HTML 用于调试
    const html = await page.content();
    const fs = await import('fs');
    fs.writeFileSync(`/workspace/projects/search-improvement/debug_${engine}_page.html`, html);

    console.error(`[DEBUG] HTML saved: ${html.length} chars`);

    // 提取结果 - 使用字符串模板注入变量
    const results = await page.evaluate(`
      (() => {
        const extracted = [];
        const limit = ${limit};
        const engine = '${engine}';
        const resultsSelector = '${resultsSelector}';
        const items = Array.from(document.querySelectorAll(resultsSelector));

        for (const item of items) {
          if (extracted.length >= limit) break;

          let title = '';
          let url = '';
          let snippet = '';

          if (engine === 'google') {
            const linkEl = item.closest('a');
            if (linkEl) {
              title = item.textContent.trim();
              url = linkEl.href;
              const parentDiv = item.closest('div[data-hveid]');
              if (parentDiv) {
                const snippetEl = parentDiv.querySelector('div[data-sncf], .VwiC3b');
                snippet = snippetEl ? snippetEl.textContent.trim() : '';
              }
            }
          } else if (engine === 'bing') {
            title = item.textContent.trim();
            const linkEl = item.closest('a');
            url = linkEl ? linkEl.href : '';
            const parentLi = item.closest('li.b_algo');
            if (parentLi) {
              const snippetEl = parentLi.querySelector('.b_caption p');
              snippet = snippetEl ? snippetEl.textContent.trim() : '';
            }
          } else if (engine === 'duckduckgo') {
            title = item.textContent.trim();
            url = item.href;
            const parentDiv = item.closest('.web-result');
            if (parentDiv) {
              const snippetEl = parentDiv.querySelector('.result__snippet');
              snippet = snippetEl ? snippetEl.textContent.trim() : '';
            }
          } else if (engine === 'baidu') {
            title = item.textContent.trim();
            url = item.href;
            const parentDiv = item.closest('.c-container');
            if (parentDiv) {
              const snippetEl = parentDiv.querySelector('.c-abstract');
              snippet = snippetEl ? snippetEl.textContent.trim() : '';
            }
          }

          if (title && url) {
            extracted.push({ title, url, snippet });
          }
        }

        return extracted;
      })()
    `);

    return results;

  } finally {
    await browser.close();
  }
}

if (!QUERY) {
  console.error('Error: No query provided');
  process.exit(1);
}

search(QUERY, ENGINE, LIMIT)
  .then(results => {
    console.log(JSON.stringify({
      success: true,
      engine: ENGINE,
      count: results.length,
      results,
    }, null, 2));
  })
  .catch(error => {
    console.error(JSON.stringify({
      success: false,
      error: error.message,
    }, null, 2));
    process.exit(1);
  });
