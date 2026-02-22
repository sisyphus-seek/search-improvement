# Brave Search 中文新闻搜索修复记录

**日期**: 2026-02-22
**问题**: Brave Search API 中文新闻搜索返回 422 错误

## 问题描述

调用 `search_news()` 时，Brave Search API 返回 422 Unprocessable Entity 错误：

```
422 Client Error: Unprocessable Entity for url: https://api.search.brave.com/res/v1/web/search?q=AI&count=3&offset=0&country=CN&text_decorations=true&spellcheck=true&safesearch=moderate&search_lang=zh-CN&freshness=pw
```

错误详情：

```json
{
  "type": "ErrorResponse",
  "error": {
    "id": "21be0791-aaad-48c4-89f9-14ee10be91dd",
    "status": 422,
    "detail": "Unable to validate request parameter(s)",
    "meta": {
      "errors": [
        {
          "type": "enum",
          "loc": ["query", "search_lang"],
          "msg": "Input should be 'ar', 'eu', 'bn', 'bg', 'ca', 'zh-hans', 'zh-hant', ..."
        }
      ]
    }
  }
}
```

## 根本原因

Brave Search API 的 `search_lang` 参数使用 **ISO 语言代码**，而非标准的地区代码（如 `zh-CN`）。

- ❌ 错误: `search_lang=zh-CN`
- ✅ 正确: `search_lang=zh-hans`（简体中文）
- ✅ 正确: `search_lang=zh-hant`（繁体中文）

## 解决方案

### 1. 修复 `search_news()` 方法

将 `search_lang="zh-CN"` 改为 `search_lang="zh-hans"`：

```python
def search_news(self, query: str, count: int = 10, freshness: str = "pw"):
    result = self.search(
        query=query,
        count=count,
        freshness=freshness,
        search_lang="zh-hans"  # 修复：使用 zh-hans 而不是 zh-CN
    )
    return result
```

### 2. 验证结果

修复后，所有测试通过：

```
=== 测试基本搜索 ===
✓ 基本搜索成功

=== 测试新闻搜索 ===
✓ 新闻搜索成功
  Web 结果: 3 个
  News 结果: 10 个

=== 测试时间新鲜度 ===
✓ 时间新鲜度搜索成功

=== 测试分页 ===
✓ 分页成功（无重复）

测试完成: 4 通过, 0 失败
```

## 受影响文件

- `src/brave_search.py` - 修复 `search_news()` 方法
- `src/unified_search.py` - 更新 `search_news()` 调用
- `src/test_brave.py` - 更新测试逻辑

## 经验教训

1. **参数文档很重要**：Brave API 文档明确说明了 `search_lang` 支持的值（`zh-hans`、`zh-hant`），但容易被误用为标准地区代码
2. **错误信息很详细**：422 错误的返回信息明确指出了 `search_lang` 参数的枚举值，应仔细阅读
3. **参数组合测试**：应单独测试每个参数，避免参数组合问题掩盖根本原因

## API 参数参考

Brave Search API 支持的 `search_lang` 值（部分）：

| 语言 | 代码 | 说明 |
|------|------|------|
| 简体中文 | `zh-hans` | Simplified Chinese |
| 繁体中文 | `zh-hant` | Traditional Chinese |
| 英语 | `en` / `en-gb` | English |
| 日语 | `jp` | Japanese |
| 韩语 | `ko` | Korean |
| 法语 | `fr` | French |
| 德语 | `de` | German |
| 西班牙语 | `es` | Spanish |

完整列表参考：https://api.search.brave.com/app/documentation
