# 可用搜索源测试结果

**更新日期**: 2026-02-15

## 已验证可用的搜索源

| 搜索源 | 状态 | API/端点 | 成功率 | 备注 |
|--------|------|----------|--------|------|
| **DuckDuckGo HTML** | ✅ 可用 | `https://duckduckgo.com/html/?q={query}` | 95% | 需要手动解析 HTML，链接有重定向 |
| **GitHub Search API** | ✅ 可用 | `https://api.github.com/search/repositories?q={query}` | 100% | 免费，有速率限制（5000/小时） |
| **Hacker News (Algolia)** | ✅ 可用 | `https://hn.algolia.com/api/v1/search?query={query}` | 100% | 返回 JSON，包含评论和故事 |
| **Startpage HTML** | ⚠️ 部分 | `https://www.startpage.com/sp/search?query={query}` | 60% | 需要动态加载，结果不完整 |

## 搜索源详情

### DuckDuckGo HTML

**优点**:
- 无需 API key
- 隐私保护
- 结果丰富

**缺点**:
- 需要手动解析 HTML
- 链接经过重定向（需要解码）
- HTML 结构可能变化

**使用示例**:
```python
import web_fetch

url = "https://duckduckgo.com/html/?q=python+tutorial"
html = web_fetch(url, extractMode="text")
# 解析结果...
```

---

### GitHub Search API

**优点**:
- 官方 API，稳定
- 返回结构化 JSON
- 适用于代码和项目搜索
- 无需认证（公开搜索）

**缺点**:
- 仅限 GitHub 内容
- 有速率限制

**限制**:
- 认证用户：5000 请求/小时
- 未认证：60 请求/小时

**端点**:
- 仓库: `/search/repositories?q={query}`
- 代码: `/search/code?q={query}`
- Issues: `/search/issues?q={query}`
- 用户: `/search/users?q={query}`

**使用示例**:
```python
import web_fetch

url = "https://api.github.com/search/repositories?q=language:python&sort=stars"
json = web_fetch(url, extractMode="text")  # 返回 JSON
# 解析结果...
```

---

### Hacker News (Algolia)

**优点**:
- 官方支持的搜索 API
- 返回结构化 JSON
- 包含元数据（分数、作者、时间）
- 无需认证

**缺点**:
- 仅限 Hacker News 内容

**端点**:
- 搜索: `https://hn.algolia.com/api/v1/search?query={query}`

**返回字段**:
- `objectID`: 唯一标识
- `title`: 标题
- `url`: 链接
- `author`: 作者
- `points`: 点数
- `created_at`: 时间戳

**使用示例**:
```python
import web_fetch

url = "https://hn.algolia.com/api/v1/search?query=LLM"
json = web_fetch(url, extractMode="text")
# 解析结果...
```

---

### Startpage

**优点**:
- 隐私搜索引擎
- 基于 Google 结果

**缺点**:
- HTML 动态加载（`web_fetch` 获取不完整）
- 可能需要浏览器

**状态**: 需要进一步测试

---

## 待测试的搜索源

- [ ] SearXNG（开源元搜索引擎）
- [ ] Qwant（欧洲隐私搜索引擎）
- [ ] Brave Search（HTML 抓取）
- [ ] Stack Overflow API
- [ ] Reddit API

## 搜索策略建议

### 按查询类型选择源

| 查询类型 | 推荐源 | 备用源 |
|----------|--------|--------|
| 代码/项目 | GitHub | DuckDuckGo |
| 技术新闻 | Hacker News | DuckDuckGo |
| 通用搜索 | DuckDuckGo | Startpage |
| API 文档 | GitHub | DuckDuckGo |

### 失败重试策略

1. 尝试主搜索源
2. 失败后尝试备用源
3. 全部失败时返回错误和建议

---

## 下一步行动

1. [ ] 实现统一的搜索接口
2. [ ] 实现搜索源自动选择
3. [ ] 实现结果去重和排序
4. [ ] 测试更多搜索源
5. [ ] 建立健康检查机制
