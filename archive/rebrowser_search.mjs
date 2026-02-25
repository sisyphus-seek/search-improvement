#!/usr/bin/env node
/**
 * 完整的浏览器检索引擎 - rebrowser-playwright 版本
 * 集成反检测措施，支持多搜索引擎
 */

import { chromium } from 'rebrowser-playwright';
import { URL } from 'url';

// 配置
const CONFIG = {
  headless: true,
  viewport: { width: 1920, height: 1080 },
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  timeout: 30000,
};

// 搜索引擎配置
const SEARCH_ENGINES = {
  google: {
    url: (q) => `https://www.google.com/search?q=${encodeURIComponent(q)}`,
    selectors: {
      results: 'div.g',
      title: 'h3',
      link: 'a',
    },
  },
  bing: {
    url: (q) => `https://www.bing.com/search?q=${encodeURIComponent(q)}`,
    selectors: {
      results: 'li.b_algo',
      title: 'h2',
      link: 'a',
    },
  },
  duckduckgo: {
    url: (q) => `https://duckduckgo.com/html/?q=${encodeURIComponent(q)}`,
    selectors: {
      results: 'div.result__body',
      title: 'a.result__a',
      link: 'a.result__a',
    },
  },
};

// 反检测脚本
const ANTI_DETECTION_SCRIPT = `
  // 删除 navigator.webdriver
  Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
  });

  // 修复 plugins
  Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5],
  });

  // 修复 languages
  Object.defineProperty(navigator, 'languages', {
    get: () => ['zh-CN', 'zh', 'en-US', 'en'],
  });

  // 添加 window.chrome
  window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {},
  };

  // 修复 permissions
  const originalQuery = window.navigator.permissions.query;
  window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
      Promise.resolve({ state: Notification.permission }) :
      originalQuery(parameters)
  );

  // 添加设备内存
  Object.defineProperty(navigator, 'deviceMemory', {
    get: () => 8,
  });

  // 添加硬件并发
  Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => 8,
  });

  console.log('[Anti-Detection] Scripts injected successfully');
`;

class BrowserSearchEngine {
  constructor(options = {}) {
    this.options = { ...CONFIG, ...options };
    this.browser = null;
    this.context = null;
    this.page = null;
    this.stats = {
      totalSearches: 0,
      successes: 0,
      failures: 0,
      byEngine: {},
    };
  }

  async start() {
    console.log('Starting browser with rebrowser-playwright...');

    // 启动浏览器
    this.browser = await chromium.launch({
      headless: this.options.headless,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
      ],
    });

    // 创建上下文
    this.context = await this.browser.newContext({
      viewport: this.options.viewport,
      userAgent: this.options.userAgent,
      locale: 'zh-CN',
      timezoneId: 'Asia/Shanghai',
      // 禁用自动化标志
      ignoreHTTPSErrors: true,
    });

    // 设置额外的 HTTP headers
    await this.context.setExtraHTTPHeaders({
      'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
    });

    // 创建页面
    this.page = await this.context.newPage();

    // 注入反检测脚本
    await this.page.addInitScript(ANTI_DETECTION_SCRIPT);

    console.log('Browser ready');
  }

  async stop() {
    console.log('Stopping browser...');
    if (this.page) await this.page.close();
    if (this.context) await this.context.close();
    if (this.browser) await this.browser.close();
    console.log('Browser stopped');
  }

  async navigate(url) {
    console.log(`Navigating to: ${url}`);
    try {
      await this.page.goto(url, {
        waitUntil: 'domcontentloaded',
        timeout: this.options.timeout,
      });
      // 等待一点时间让动态内容加载
      await this.page.waitForTimeout(1000);
      return true;
    } catch (error) {
      console.error(`Navigation failed: ${error.message}`);
      return false;
    }
  }

  async search(query, engine = 'duckduckgo', limit = 10) {
    this.stats.totalSearches++;
    if (!this.stats.byEngine[engine]) {
      this.stats.byEngine[engine] = { successes: 0, failures: 0 };
    }

    console.log(`\nSearching on ${engine}: ${query}`);

    const engineConfig = SEARCH_ENGINES[engine];
    if (!engineConfig) {
      console.error(`Unknown search engine: ${engine}`);
      this.stats.failures++;
      this.stats.byEngine[engine].failures++;
      return [];
    }

    // 导航到搜索页面
    const url = engineConfig.url(query);
    const success = await this.navigate(url);

    if (!success) {
      this.stats.failures++;
      this.stats.byEngine[engine].failures++;
      return [];
    }

    // 检查是否被重定向到 CAPTCHA 或错误页面
    const currentUrl = this.page.url();
    if (currentUrl.includes('sorry') || currentUrl.includes('captcha')) {
      console.warn(`CAPTCHA detected on ${engine}`);
      this.stats.failures++;
      this.stats.byEngine[engine].failures++;
      return [];
    }

    // 提取结果
    try {
      const results = await this.extractResults(engineConfig, limit);
      this.stats.successes++;
      this.stats.byEngine[engine].successes++;
      console.log(`Found ${results.length} results`);
      return results;
    } catch (error) {
      console.error(`Failed to extract results: ${error.message}`);
      this.stats.failures++;
      this.stats.byEngine[engine].failures++;
      return [];
    }
  }

  async extractResults(engineConfig, limit) {
    const results = [];

    try {
      // 根据搜索引擎的不同使用不同的提取策略
      if (engineConfig === SEARCH_ENGINES.duckduckgo) {
        // DuckDuckGo 特定提取
        const links = await this.page.$$eval('a.result__a', (elements) => {
          return elements.map((el) => ({
            title: el.textContent?.trim() || '',
            href: el.href,
          }));
        });

        for (const link of links.slice(0, limit)) {
          // DuckDuckGo 可能使用重定向 URL
          let url = link.href;
          if (url.includes('duckduckgo.com/l/?uddg=')) {
            try {
              const urlObj = new URL(url);
              const uddg = urlObj.searchParams.get('uddg');
              if (uddg) {
                url = decodeURIComponent(uddg);
              }
            } catch (e) {
              // 保持原 URL
            }
          }

          results.push({
            title: link.title,
            url: url,
            source: 'DuckDuckGo',
          });
        }
      } else if (engineConfig === SEARCH_ENGINES.bing) {
        // Bing 特定提取
        const resultsDivs = await this.page.$$('li.b_algo');

        for (const div of resultsDivs.slice(0, limit)) {
          try {
            const link = await div.$('h2 a');
            if (link) {
              const title = await link.textContent();
              const url = await link.getAttribute('href');
              if (title && url) {
                results.push({
                  title: title.trim(),
                  url,
                  source: 'Bing',
                });
              }
            }
          } catch (e) {
            // 跳过无效结果
          }
        }
      } else if (engineConfig === SEARCH_ENGINES.google) {
        // Google 特定提取
        const resultsDivs = await this.page.$$('div.g');

        for (const div of resultsDivs.slice(0, limit)) {
          try {
            const link = await div.$('h3 a');
            if (link) {
              const title = await link.textContent();
              const url = await link.getAttribute('href');

              // Google 可能使用重定向 URL
              let cleanUrl = url;
              if (url && url.startsWith('/url?q=')) {
                try {
                  const u = new URL('https://www.google.com' + url);
                  cleanUrl = u.searchParams.get('q');
                } catch (e) {
                  cleanUrl = url;
                }
              }

              if (title && cleanUrl) {
                results.push({
                  title: title.trim(),
                  url: cleanUrl,
                  source: 'Google',
                });
              }
            }
          } catch (e) {
            // 跳过无效结果
          }
        }
      }

    } catch (error) {
      console.error(`Error during extraction: ${error.message}`);
    }

    return results;
  }

  async searchAll(query, engines = ['duckduckgo', 'bing'], limitPerEngine = 5, totalLimit = 10) {
    console.log(`\nSearching across ${engines.join(', ')}: ${query}`);

    const allResults = [];

    for (const engine of engines) {
      try {
        const results = await this.search(query, engine, limitPerEngine);
        allResults.push(...results);
      } catch (error) {
        console.error(`Error searching ${engine}: ${error.message}`);
      }
    }

    // 去重（按 URL）
    const seenUrls = new Set();
    const uniqueResults = [];

    for (const result of allResults) {
      if (result.url && !seenUrls.has(result.url)) {
        seenUrls.add(result.url);
        uniqueResults.push(result);
      }
    }

    return uniqueResults.slice(0, totalLimit);
  }

  getStats() {
    return {
      totalSearches: this.stats.totalSearches,
      successRate: this.stats.totalSearches > 0
        ? (this.stats.successes / this.stats.totalSearches * 100).toFixed(2) + '%'
        : '0%',
      byEngine: this.stats.byEngine,
    };
  }

  async getSnapshot() {
    return await this.page.accessibility.snapshot();
  }

  async screenshot(path) {
    await this.page.screenshot({ path, fullPage: false });
  }
}

// 主函数
async function main() {
  const engine = new BrowserSearchEngine({
    headless: true,
  });

  try {
    await engine.start();

    // 测试 1: 单引擎搜索
    console.log('\n' + '='.repeat(60));
    console.log('Test 1: DuckDuckGo - playwright bot bypass');
    console.log('='.repeat(60));

    const results1 = await engine.search('playwright bot bypass', 'duckduckgo', 5);
    for (let i = 0; i < results1.length; i++) {
      const r = results1[i];
      console.log(`\n${i + 1}. ${r.title}`);
      console.log(`   URL: ${r.url}`);
    }

    // 测试 2: 多引擎搜索
    console.log('\n' + '='.repeat(60));
    console.log('Test 2: Multi-engine - AI agents');
    console.log('='.repeat(60));

    const results2 = await engine.searchAll('AI agents', ['duckduckgo', 'bing'], 5, 10);
    for (let i = 0; i < results2.length; i++) {
      const r = results2[i];
      console.log(`\n${i + 1}. ${r.title}`);
      console.log(`   [${r.source}] ${r.url}`);
    }

    // 测试 3: Bing
    console.log('\n' + '='.repeat(60));
    console.log('Test 3: Bing - rebrowser-playwright');
    console.log('='.repeat(60));

    const results3 = await engine.search('rebrowser-playwright', 'bing', 5);
    for (let i = 0; i < results3.length; i++) {
      const r = results3[i];
      console.log(`\n${i + 1}. ${r.title}`);
      console.log(`   URL: ${r.url}`);
    }

    // 统计信息
    console.log('\n' + '='.repeat(60));
    console.log('Statistics');
    console.log('='.repeat(60));
    console.log(JSON.stringify(engine.getStats(), null, 2));

  } finally {
    await engine.stop();
  }
}

// 导出供其他模块使用
export { BrowserSearchEngine };

// 如果直接运行此文件
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
