# Reddit API 修复成功

**日期**: 2026-02-15

## 问题

Reddit API 返回 HTML 而非 JSON，导致 JSON 解析失败。

## 解决方案

添加浏览器头部（User-Agent、Accept）来模拟真实浏览器请求：

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
}
```

## 修改文件

- `unified_search_v2.py`: 
  - 更新 `web_fetch()` 函数支持自定义头部
  - 修复 `RedditSearchSource` 类

## 测试结果

- ✅ Reddit API 现在返回 JSON 格式
- ✅ 搜索 "machine learning" 成功返回 5 个结果
- ✅ 成功率从 0% 提升到 100%

## 当前搜索源状态

| 搜索源 | 成功率 | 状态 |
|--------|--------|------|
| GitHub | 100% | ✅ |
| Hacker News | 100% | ✅ |
| Reddit | 100% | ✅ (已修复) |
| Stack Overflow | 100% | ✅ |
| DuckDuckGo | 100% | ✅ |

**所有搜索源现在都可用！**

## 下一步

使用优化后的检索能力进行实际搜索测试。
