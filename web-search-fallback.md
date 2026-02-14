# 网络搜索备选方案

**日期**: 2026-02-15
**上下文**: 传统搜索引擎 API 缺失，浏览器自动化被反爬虫拦截

## 问题
- `web_search` 需要 Brave Search API key（未配置）
- Google、Bing 等通过浏览器访问会触发人机验证
- 第三方搜索引擎爬虫库（如 Search-Engines-Scraper）选择器失效

## 可用方案：DuckDuckGo HTML 抓取

### 实现方式
```python
# 使用 web_fetch 直接抓取 DuckDuckGo 搜索结果
url = "https://duckduckgo.com/html/?q={query}"
html = web_fetch(url, extractMode="text")

# 手动解析结果（正则匹配标题、链接）
# DuckDuckGo 返回的链接格式：//duckduckgo.com/l/?uddg=<encoded_url>
```

### 优点
- ✅ DuckDuckGo 对爬虫相对友好
- ✅ 直接 HTTP 请求，无需浏览器
- ✅ 不依赖易失效的 CSS 选择器
- ✅ 稳定可用

### 缺点
- ⚠️ 需要手动解析 HTML 结构
- ⚠️ 链接经过 DuckDuckGo 重定向（需要解码 uddg 参数）
- ⚠️ 仅限 DuckDuckGo，Google/Bing 仍不可用

## 测试结果
- ✅ DuckDuckGo HTML 抓取：成功
- ❌ Search-Engines-Scraper (Bing/Yahoo/DuckDuckGo)：选择器失效或反爬虫
- ❌ 浏览器自动化 (Google)：人机验证拦截

## 结论
在获得成熟搜索 API 或解决反爬虫问题前，此方案可作为**备选搜索手段**。

**使用场景**：需要快速搜索且只需结果摘要时。

**不适用**：需要完整搜索结果页面、高级筛选、或依赖 Google/Bing 的场景。
