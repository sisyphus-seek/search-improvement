#!/usr/bin/env python3
"""
增强版 Google 搜索 - 使用 rebrowser-playwright 绕过机器人检测

这个模块使用 Node.js + rebrowser-playwright 来执行 Google 搜索，
能够绕过 CAPTCHA 和其他机器人检测。
"""

import json
import subprocess
import tempfile
import os
from typing import List, Dict, Optional


class GoogleSearchResult:
    """Google 搜索结果"""
    def __init__(self, title: str, url: str, snippet: str = ""):
        self.title = title
        self.url = url
        self.snippet = snippet

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet
        }


class EnhancedGoogleSearch:
    """增强版 Google 搜索器"""

    def __init__(self):
        self.node_script = self._create_node_script()

    def _create_node_script(self) -> str:
        """创建 Node.js 脚本模板"""
        return '''import { chromium } from 'rebrowser-playwright';

async function googleSearch(query, limit) {
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
  });

  const page = await context.newPage();

  try {
    // 访问 Google
    await page.goto('https://www.google.com', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(1000);

    // 检查是否有 CAPTCHA
    const hasCaptcha = await page.evaluate(() => {
      return !!document.querySelector('#captcha-form');
    });

    if (hasCaptcha) {
      throw new Error('Google 触发了 CAPTCHA');
    }

    // 执行搜索
    const searchInput = await page.$('textarea[name="q"]');
    if (!searchInput) {
      throw new Error('找不到搜索框');
    }

    await searchInput.fill(query);
    await page.keyboard.press('Enter');

    // 等待搜索结果加载
    await page.waitForTimeout(2000);

    // 提取搜索结果
    const results = await page.evaluate((limit) => {
      const items = Array.from(document.querySelectorAll('div[data-hveid]'));
      const extracted = [];

      for (const item of items) {
        if (extracted.length >= limit) break;

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

      return extracted;
    }, limit);

    return results;

  } finally {
    await browser.close();
  }
}

// 从命令行参数读取查询
const query = process.argv[2];
const limit = parseInt(process.argv[3]) || 10;

if (!query) {
  console.error('Error: No query provided');
  process.exit(1);
}

googleSearch(query, limit)
  .then(results => {
    console.log(JSON.stringify(results, null, 2));
  })
  .catch(error => {
    console.error(JSON.stringify({ error: error.message }));
    process.exit(1);
  });
'''

    def search(self, query: str, limit: int = 10) -> List[GoogleSearchResult]:
        """
        执行 Google 搜索

        Args:
            query: 搜索查询
            limit: 返回结果数量

        Returns:
            搜索结果列表
        """
        # 创建临时脚本文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as f:
            script_path = f.name
            f.write(self.node_script)

        try:
            # 运行 Node.js 脚本
            result = subprocess.run(
                ['node', script_path, query, str(limit)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd='/workspace/projects/search-improvement'
            )

            if result.returncode != 0:
                return []

            # 解析结果
            try:
                data = json.loads(result.stdout)
                if 'error' in data:
                    return []
                results = []
                for item in data:
                    results.append(GoogleSearchResult(
                        title=item.get('title', ''),
                        url=item.get('url', ''),
                        snippet=item.get('snippet', '')
                    ))
                return results
            except json.JSONDecodeError:
                return []

        finally:
            # 清理临时文件
            if os.path.exists(script_path):
                os.remove(script_path)


# 测试代码
if __name__ == "__main__":
    searcher = EnhancedGoogleSearch()

    print("=" * 60)
    print("增强版 Google 搜索测试")
    print("=" * 60)

    queries = [
        "playwright bot bypass",
        "python async await",
        "AI agents latest",
    ]

    for query in queries:
        print(f"\n搜索: {query}")
        results = searcher.search(query, limit=5)

        if results:
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r.title}")
                print(f"     {r.url}")
                if r.snippet:
                    print(f"     {r.snippet[:100]}...")
        else:
            print("  无结果")

    print("\n" + "=" * 60)
