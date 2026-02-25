#!/usr/bin/env node
/**
 * 隐形浏览器检索引擎 v2
 * 优化版：URL 解析、稳定性提升、混合搜索策略
 */

import { chromium } from 'playwright';

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

  console.log('[Anti-Detection] Scripts injected');
`;

/**
 * 解析 Bing 重定向 URL
 * Bing 返回: https://www.bing.com/ck/a?!&&p=...&u=a1aHR0cHM6Ly...
 * 提取 u 参数并解码
 */
function parseBingRedirectUrl(url) {
  try {
    if (!url.includes('bing.com/ck/a')) return url;

    // 提取 u 参数
    const uMatch = url.match(/[?&]u=([a-zA-Z0-9_-]+)/);
    if (!uMatch) return url;

    // Base64 解码
    const encoded = uMatch[1];
    // u 参数通常是 base64 编码的 URL
    let decoded = Buffer.from(encoded, 'base64').toString('utf-8');

    // 清理可能的 URL 前缀
    decoded = decoded.replace(/^[a-z]+:/, '');

    return decoded;
  } catch (e) {
    console.warn(`Failed to parse Bing URL: ${e.message}`);
    return url;
  }
}

/**
 * 解析 DuckDuckGo 重定向 URL
 * DuckDuckGo 返回: https://duckduckgo.com/l/?uddg=<encoded_url>
 */
function parseDuckDuckGoRedirectUrl(url) {
  try {
    if (!url.includes('duckduckgo.com/l/?uddg=')) return url;

    const urlObj = new URL(url);
    const uddg = urlObj.searchParams.get('uddg');

    if (uddg) {
      return decodeURIComponent(uddg);
    }

    return url;
  } catch (e) {
    console.warn(`Failed to parse DuckDuckGo URL: ${e.message}`);
    return url;
  }
}

class StealthSearchEngine {
  constructor(options = {}) {
    this.options = {
      headless: true,
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      timeout: 30000,
      retryCount: 2,
      retryDelay: 2000,
      ...options,
    };
    this.browser = null;
    this.context = null;
    this.page = null;
    this.stats = {
      totalSearches: 0,
      successes: 0,
      failures: 0,
      retries: 0,
      byEngine: {},
    };
  }

  async start() {
    console.log('Starting stealth browser v2...');

    this.browser = await chromium.launch({
      headless: this.options.headless,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
        '--disable-features=IsolateOrigins,site-per-process',
      ],
    });

    this.context = await this.browser.newContext({
      viewport: this.options.viewport,
      userAgent: this.options.userAgent,
      locale: 'zh-CN',
      timezoneId: 'Asia/Shanghai',
      ignoreHTTPSErrors: true,
    });

    await this.context.setExtraHTTPHeaders({
      'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'none',
      'Sec-Fetch-User': '?1',
    });

    this.page = await this.context.newPage();
    await this.page.addInitScript(ANTI_DETECTION_SCRIPT);

    console.log('Stealth browser v2 ready');
  }

  async stop() {
    console.log('Stopping stealth browser v2...');
    if (this.page) await this.page.close();
    if (this.context) await this.context.close();
    if (this.browser) await this.browser.close();
    console.log('Stopped');
  }

  /**
   * 带重试的导航
   */
  async navigateWithRetry(url, retries = this.options.retryCount) {
    for (let i = 0; i < retries; i++) {
      try {
        console.log(`Navigating to: ${url} (attempt ${i + 1}/${retries})`);

        await this.page.goto(url, {
          waitUntil: 'domcontentloaded',
          timeout: this.options.timeout,
        });

        // 等待内容加载
        await this.page.waitForTimeout(1500);

        // 检查是否被重定向到错误页面
        const currentUrl = this.page.url();
        if (currentUrl.includes('error') || currentUrl.includes('blocked')) {
          throw new Error(`Blocked or error page: ${currentUrl}`);
        }

        return true;
      } catch (error) {
        console.warn(`Navigation attempt ${i + 1} failed: ${error.message}`);

        if (i < retries - 1) {
          this.stats.retries++;
          await this.page.waitForTimeout(this.options.retryDelay);
        } else {
          console.error(`Navigation failed after ${retries} attempts`);
          return false;
        }
      }
    }
    return false;
  }

  async searchDuckDuckGo(query, limit = 10) {
    this.stats.totalSearches++;
    if (!this.stats.byEngine.duckduckgo) {
      this.stats.byEngine.duckduckgo = { successes: 0, failures: 0 };
    }

    console.log(`\nSearching DuckDuckGo: ${query}`);

    const url = `https://duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
    const success = await this.navigateWithRetry(url);

    if (!success) {
      this.stats.failures++;
      this.stats.byEngine.duckduckgo.failures++;
      return [];
    }

    // 检查 CAPTCHA
    const currentUrl = this.page.url();
    if (currentUrl.includes('captcha') || currentUrl.includes('challenge')) {
      console.warn('CAPTCHA detected on DuckDuckGo');
      this.stats.failures++;
      this.stats.byEngine.duckduckgo.failures++;
      return [];
    }

    // 提取结果
    try {
      const results = await this.page.$$eval('a.result__a', (elements) => {
        return elements.map((el) => ({
          title: el.textContent?.trim() || '',
          href: el.href,
        }));
      });

      const cleanedResults = [];
      for (const link of results.slice(0, limit)) {
        let url = parseDuckDuckGoRedirectUrl(link.href);

        cleanedResults.push({
          title: link.title,
          url,
          source: 'DuckDuckGo',
        });
      }

      this.stats.successes++;
      this.stats.byEngine.duckduckgo.successes++;
      console.log(`Found ${cleanedResults.length} results`);
      return cleanedResults;
    } catch (error) {
      console.error(`DuckDuckGo extraction failed: ${error.message}`);
      this.stats.failures++;
      this.stats.byEngine.duckduckgo.failures++;
      return [];
    }
  }

  async searchBing(query, limit = 10) {
    this.stats.totalSearches++;
    if (!this.stats.byEngine.bing) {
      this.stats.byEngine.bing = { successes: 0, failures: 0 };
    }

    console.log(`\nSearching Bing: ${query}`);

    const url = `https://www.bing.com/search?q=${encodeURIComponent(query)}`;
    const success = await this.navigateWithRetry(url);

    if (!success) {
      this.stats.failures++;
      this.stats.byEngine.bing.failures++;
      return [];
    }

    // 检查 CAPTCHA
    const currentUrl = this.page.url();
    if (currentUrl.includes('captcha') || currentUrl.includes('challenge')) {
      console.warn('CAPTCHA detected on Bing');
      this.stats.failures++;
      this.stats.byEngine.bing.failures++;
      return [];
    }

    // 提取结果
    try {
      const results = await this.page.$$eval('li.b_algo', (items) => {
        const extracted = [];
        items.forEach((item) => {
          const link = item.querySelector('h2 a');
          if (link) {
            extracted.push({
              title: link.textContent?.trim() || '',
              href: link.href,
            });
          }
        });
        return extracted;
      });

      const cleanedResults = [];
      for (const r of results.slice(0, limit)) {
        let url = parseBingRedirectUrl(r.href);

        cleanedResults.push({
          title: r.title,
          url,
          source: 'Bing',
        });
      }

      this.stats.successes++;
      this.stats.byEngine.bing.successes++;
      console.log(`Found ${cleanedResults.length} results`);
      return cleanedResults;
    } catch (error) {
      console.error(`Bing extraction failed: ${error.message}`);
      this.stats.failures++;
      this.stats.byEngine.bing.failures++;
      return [];
    }
  }

  /**
   * 混合搜索策略：优先 API，失败时降级到浏览器
   */
  async searchWithFallback(query, preferredEngines = ['duckduckgo', 'bing'], limit = 10) {
    console.log(`\n=== Hybrid Search: ${query} ===`);

    const allResults = [];

    // 尝试浏览器搜索
    for (const engine of preferredEngines) {
      try {
        let results;
        if (engine === 'duckduckgo') {
          results = await this.searchDuckDuckGo(query, Math.ceil(limit / 2));
        } else if (engine === 'bing') {
          results = await this.searchBing(query, Math.ceil(limit / 2));
        }

        if (results && results.length > 0) {
          allResults.push(...results);
        }
      } catch (error) {
        console.error(`Error on ${engine}: ${error.message}`);
      }

      // 如果已经有足够结果，停止
      if (allResults.length >= limit) {
        break;
      }
    }

    // 去重
    const seenUrls = new Set();
    const uniqueResults = [];

    for (const result of allResults) {
      if (result.url && !seenUrls.has(result.url)) {
        seenUrls.add(result.url);
        uniqueResults.push(result);
      }
    }

    return uniqueResults.slice(0, limit);
  }

  getStats() {
    return {
      totalSearches: this.stats.totalSearches,
      successes: this.stats.successes,
      failures: this.stats.failures,
      retries: this.stats.retries,
      successRate: this.stats.totalSearches > 0
        ? ((this.stats.successes / this.stats.totalSearches) * 100).toFixed(2) + '%'
        : '0%',
      byEngine: this.stats.byEngine,
    };
  }
}

// 主函数
async function main() {
  const engine = new StealthSearchEngine({ headless: true });

  try {
    await engine.start();

    // 测试 1: DuckDuckGo
    console.log('\n' + '='.repeat(60));
    console.log('Test 1: DuckDuckGo - playwright bot bypass');
    console.log('='.repeat(60));
    const r1 = await engine.searchDuckDuckGo('playwright bot bypass', 5);
    for (let i = 0; i < r1.length; i++) {
      console.log(`\n${i+1}. ${r1[i].title}\n   URL: ${r1[i].url}`);
    }

    // 测试 2: Bing
    console.log('\n' + '='.repeat(60));
    console.log('Test 2: Bing - AI agents');
    console.log('='.repeat(60));
    const r2 = await engine.searchBing('AI agents', 5);
    for (let i = 0; i < r2.length; i++) {
      console.log(`\n${i+1}. ${r2[i].title}\n   URL: ${r2[i].url}`);
    }

    // 测试 3: 混合搜索
    console.log('\n' + '='.repeat(60));
    console.log('Test 3: Hybrid Search - browser automation');
    console.log('='.repeat(60));
    const r3 = await engine.searchWithFallback('browser automation', ['duckduckgo', 'bing'], 10);
    for (let i = 0; i < r3.length; i++) {
      console.log(`\n${i+1}. ${r3[i].title}\n   [${r3[i].source}] ${r3[i].url}`);
    }

    // 统计
    console.log('\n' + '='.repeat(60));
    console.log('Statistics');
    console.log('='.repeat(60));
    console.log(JSON.stringify(engine.getStats(), null, 2));

  } finally {
    await engine.stop();
  }
}

main().catch(console.error);
