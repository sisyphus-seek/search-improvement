# 浏览器检索引擎 - 完整架构

## 概述

这是一个完整的浏览器检索引擎，支持多搜索引擎、反检测措施、结果提取和缓存。基于 Playwright 构建，可扩展支持更多搜索引擎。

## 核心组件

### 1. BrowserSession
管理浏览器生命周期和反检测措施。

**关键特性**：
- 基于 Playwright 的浏览器控制
- 注入反检测脚本（navigator.webdriver、window.chrome 等）
- 配置 User-Agent、viewport、HTTP headers
- 支持代理（可选）

**反检测脚本**：
```javascript
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
```

### 2. ResultExtractor
从搜索结果页面提取结构化数据。

**支持的搜索引擎**：
- Google
- Bing
- DuckDuckGo
- Baidu

**提取策略**：
- 使用 CSS 选择器定位结果元素
- 处理重定向 URL（DuckDuckGo、Google）
- 提取标题、URL、摘要

### 3. BrowserSearchEngine
统一搜索引擎接口。

**API**：
```python
await engine.start()                          # 启动浏览器
await engine.search(query, engine, limit)      # 单引擎搜索
await engine.search_all(query, engines, ...)   # 多引擎搜索
engine.get_stats()                            # 获取统计信息
await engine.stop()                           # 停止浏览器
```

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                  User / Alphonso Agent                  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              BrowserSearchEngine (API)                  │
│  - search()                                             │
│  - search_all()                                        │
│  - get_stats()                                         │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│              BrowserSession                             │
│  - start() / stop()                                    │
│  - navigate(url)                                       │
│  - Anti-detection scripts                              │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│            ResultExtractor                              │
│  - extract_google_results()                            │
│  - extract_bing_results()                              │
│  - extract_duckduckgo_results()                        │
│  - extract_baidu_results()                             │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│              Search Engines                             │
│  - Google                                               │
│  - Bing                                                 │
│  - DuckDuckGo                                           │
│  - Baidu                                                │
└─────────────────────────────────────────────────────────┘
```

## 文件结构

```
/workspace/projects/search-improvement/
├── browser_search_engine.py      # Python 版本（简化，使用 curl）
├── rebrowser_search.mjs          # Node.js 版本（rebrowser-playwright）
├── stealth_search.mjs            # Node.js 版本（标准 Playwright + 反检测）
└── BROWSER_SEARCH_ENGINE.md       # 本文档
```

## 使用示例

### Python 版本（简化）

```python
import asyncio
from browser_search_engine import BrowserSearchEngine, SearchEngine

async def main():
    engine = BrowserSearchEngine()
    await engine.start()

    # DuckDuckGo 搜索
    results = await engine.search("playwright bot bypass", SearchEngine.DUCKDUCKGO, limit=5)

    # 多引擎搜索
    results = await engine.search_all(
        "AI agents",
        engines=[SearchEngine.DUCKDUCKGO, SearchEngine.BING],
        limit_per_engine=3,
        total_limit=10
    )

    await engine.stop()

asyncio.run(main())
```

### Node.js 版本（推荐）

```javascript
import { StealthSearchEngine } from './stealth_search.mjs';

const engine = new StealthSearchEngine({ headless: true });

await engine.start();

// 单引擎搜索
const results1 = await engine.searchDuckDuckGo('playwright bot bypass', 5);

// 多引擎搜索
const results2 = await engine.searchAll(
  'AI agents',
  ['duckduckgo', 'bing'],
  5,  // limitPerEngine
  10  // totalLimit
);

await engine.stop();
```

## 反检测措施

### 1. JavaScript 层面
- 删除 `navigator.webdriver`
- 修复 `navigator.plugins`
- 修复 `navigator.languages`
- 添加 `window.chrome`
- 修复 `navigator.permissions`

### 2. HTTP 层面
- 真实 User-Agent
- Accept-Language 设置
- DNT header
- Connection: keep-alive

### 3. 浏览器层面
- 禁用 automation flags
- 禁用 blink-features=AutomationControlled
- 设置 viewport
- 设置 locale 和 timezone

## 性能优化

### 1. 并发搜索
多引擎搜索可以并发执行（使用 `Promise.all`）：

```javascript
const results = await Promise.all([
  engine.searchDuckDuckGo(query, limit),
  engine.searchBing(query, limit),
]);
```

### 2. 结果缓存
可以添加缓存层，避免重复搜索相同查询：

```javascript
const cache = new Map();

async function getCachedSearch(query, engine) {
  const key = `${engine}:${query}`;
  if (cache.has(key)) {
    return cache.get(key);
  }
  const results = await engine.search(query, engine);
  cache.set(key, results);
  return results;
}
```

### 3. 超时控制
为每个搜索操作设置合理的超时：

```javascript
try {
  await page.goto(url, { timeout: 30000 });
} catch (error) {
  if (error.name === 'TimeoutError') {
    console.log('Search timeout, skipping...');
  }
}
```

## 统计信息

引擎会自动记录统计信息：

```json
{
  "totalSearches": 10,
  "successRate": "80.00%",
  "byEngine": {
    "duckduckgo": {
      "successes": 4,
      "failures": 1
    },
    "bing": {
      "successes": 4,
      "failures": 1
    }
  }
}
```

## 扩展新搜索引擎

添加新的搜索引擎只需三步：

### 1. 定义 URL 模板

```javascript
SEARCH_ENGINES.newengine = {
  url: (q) => `https://newengine.com/search?q=${encodeURIComponent(q)}`,
  selectors: {
    results: 'div.result',
    title: 'h2',
    link: 'a',
  },
};
```

### 2. 实现提取方法

```javascript
async searchNewEngine(query, limit = 10) {
  const url = `https://newengine.com/search?q=${encodeURIComponent(query)}`;
  await this.navigate(url);

  const results = await this.page.$$eval('div.result', (items) => {
    return items.map(item => ({
      title: item.querySelector('h2')?.textContent?.trim(),
      href: item.querySelector('a')?.href,
    }));
  });

  return results.map(r => ({
    title: r.title,
    url: r.href,
    source: 'NewEngine',
  }));
}
```

### 3. 集成到 searchAll()

```javascript
async searchAll(query, engines = ['duckduckgo', 'bing', 'newengine'], ...) {
  // ... 现有代码
  if (engine === 'newengine') {
    allResults.push(...await this.searchNewEngine(query, limitPerEngine));
  }
  // ...
}
```

## 限制与已知问题

### 1. CAPTCHA
- Google 对自动化访问有严格检测
- 即使使用反检测脚本，仍可能触发 CAPTCHA
- 解决方案：
  - 使用代理池轮换 IP
  - 降级到 DuckDuckGo（更宽松）
  - 使用 API 搜索作为后备

### 2. IP 信誉
- 当前 IP (77.93.89.67) 可能被标记为异常流量
- 解决方案：
  - 使用住宅代理
  - 降低请求频率
  - 添加请求间的随机延迟

### 3. 性能
- 浏览器启动较慢
- 每次搜索需要完整页面加载
- 解决方案：
  - 保持浏览器实例运行（不频繁启动/停止）
  - 使用轻量级模式（headless）
  - 并发搜索

## 下一步

### 1. 代理支持
```javascript
const context = await browser.newContext({
  proxy: {
    server: 'http://proxy.example.com:8080',
    username: 'user',
    password: 'pass',
  },
});
```

### 2. Cookie 持久化
```javascript
// 启动时加载 cookies
const context = await browser.newContext();
await context.addCookies(cookies);

// 停止前保存 cookies
const cookies = await context.cookies();
```

### 3. 分布式搜索
- 多实例并行搜索
- 任务队列
- 结果聚合

## 总结

这个浏览器检索引擎提供了：
- ✅ 多搜索引擎支持
- ✅ 反检测措施
- ✅ 统一 API
- ✅ 统计信息
- ✅ 可扩展架构

**道（核心能力）**：深度渲染、DOM 解析、反爬虫绕过
**术（具体实现）**：Playwright、反检测脚本、结果提取

通过结合浏览器能力和 API 搜索，构建了一个完整的检索系统。
