# Search Improvement Project

优化网络检索能力的实验项目。

## 目标
通过持续迭代改进搜索能力，解决以下问题：
- 传统搜索引擎 API 缺失或受限
- 浏览器自动化被反爬虫拦截
- 第三方爬虫库选择器失效
- 搜索结果质量不稳定

## 当前方案 (v3) - 双引擎智能搜索

### 核心架构

```
┌─────────────────────────────────────────────────────────┐
│              Unified Search Interface                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │   Anspire    │  │    Brave     │  │ DuckDuckGo│  │
│  │   AI 增强    │  │   隐私优先   │  │  备选     │  │
│  └──────────────┘  └──────────────┘  └───────────┘  │
│         ▲                  ▲                  ▲        │
│         │                  │                  │        │
│  ┌──────┴──────────────────┴──────────────────┴────┐│
│  │         Intent Recognition & Cache               ││
│  │  - 站内搜索 → Anspire (多站支持)               ││
│  │  - 时间范围 → Anspire (稳定)                   ││
│  │  - 新闻搜索 → Anspire → Brave                 ││
│  │  - 技术搜索 → Anspire (AI 增强)               ││
│  │  - 通用搜索 → Anspire → Brave → DuckDuckGo    ││
│  └───────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### 搜索引擎对比

| 引擎 | 优先级 | 状态 | 特点 | 限制 |
|------|--------|------|------|------|
| Anspire AI Search | 1 | ✅ 已启用 | AI 增强结果、站内搜索（多站）、时间范围、50 条结果 | 查询 ≤64 字符 |
| Brave Search | 2 | ✅ 已启用 | 隐私优先、快速响应、20 条结果 | 最多 20 条结果 |
| DuckDuckGo | 3 | 🔄 待启用 | 无需 API Key、浏览器自动化 | 验证码敏感 |

### 核心功能

#### 1. 统一搜索接口

```python
from src.unified_search import UnifiedSearchClient, SearchEngine

client = UnifiedSearchClient()

# 默认引擎（Anspire）
result = client.search("查询内容", count=10)

# 指定引擎
result = client.search("查询内容", engine=SearchEngine.BRAVE)

# 意图分析
analysis = client.analyze_intent("site:github.com openclaw")
```

#### 2. 搜索结果缓存

- **位置**: `~/.workspace/cache/search/`
- **TTL**: 24 小时
- **Key**: MD5(查询 + 参数)
- **自动清理**: 过期自动删除

#### 3. 搜索意图识别

支持 6 种意图类型：

| 意图 | 特征 | 引擎选择 |
|------|------|----------|
| 站内搜索 | `site:domain` | Anspire（支持多站） |
| 多站搜索 | 多个 `site:` | Anspire（最多 20 站） |
| 时间范围 | `from:`, `to:` 等时间关键词 | Anspire |
| 技术搜索 | API、Python、代码相关 | Anspire（AI 增强） |
| 新闻搜索 | 新闻相关 | Anspire → Brave |
| 通用搜索 | 其他查询 | Anspire → Brave → DuckDuckGo |

#### 4. 智能引擎选择

- **默认**: Anspire（功能更全，AI 增强）
- **回退顺序**: Anspire → Brave → DuckDuckGo
- **自动切换**: 根据查询类型和结果质量自动选择

## API 参数对比

### Anspire

| 参数 | 说明 | 限制 |
|------|------|------|
| query | 搜索查询 | ≤64 字符 |
| top_k | 返回条数 | 10/20/30/40/50 |
| Insite | 站内搜索 | 最多 20 站 |
| FromTime | 起始时间 | ISO 8601 格式 |
| ToTime | 结束时间 | ISO 8601 格式 |

### Brave

| 参数 | 说明 | 限制 |
|------|------|------|
| q | 搜索查询 | 无限制 |
| count | 返回条数 | ≤20 |
| result_filter | 结果类型 | web/news（⚠️ 中文搜索不建议） |
| freshness | 时间新鲜度 | p1d/pw/pm/py |
| country | 结果国家 | CN/US |
| search_lang | 搜索语言 | zh-hans/zh-hant/en（⚠️ 非 zh-CN） |
| safesearch | 安全搜索 | strict/moderate/off |

## 项目结构

```
.
├── src/
│   ├── unified_search.py         # 统一搜索引擎接口
│   ├── engines/
│   │   ├── anspire_search.py    # Anspire 封装（含缓存+意图）
│   │   └── brave_search.py      # Brave 封装
│   ├── utils/
│   │   ├── search_cache.py       # 搜索结果缓存模块
│   │   └── search_intent.py     # 搜索意图识别模块
│   └── tests/
│       ├── test_anspire.py       # Anspire 测试
│       ├── test_brave.py         # Brave 测试
│       └── test_search_enhancements.py  # 增强功能测试
├── docs/
│   ├── search-capabilities.md    # 搜索能力完整文档
│   ├── fix-time-format-2026-02-22.md  # 时间格式修复记录
│   └── fix-brave-search-lang-2026-02-22.md  # Brave 修复记录
├── requirements.txt              # Python 依赖
├── .gitignore                  # Git 忽略规则
└── README.md                    # 本文件
```

## 安装和使用

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API Keys

将 API Keys 存储在环境变量中：

```bash
# Anspire API Key
export ANSPIRE_API_KEY="your-anspire-api-key"

# Brave Search API Key
export BRAVE_API_KEY="your-brave-api-key"
```

### 运行测试

```bash
# 测试 Anspire
cd src/tests
python test_anspire.py

# 测试 Brave
python test_brave.py

# 测试增强功能
python test_search_enhancements.py
```

### 使用示例

```python
# 基础搜索
from src.unified_search import UnifiedSearchClient
client = UnifiedSearchClient()
result = client.search("人工智能", count=10)

# 站内搜索
result = client.search("openclaw", count=10)

# 多站搜索
from src.engines.anspire_search import AnspireSearchAgent
agent = AnspireSearchAgent()
result = agent.search_multi_site(
    "API",
    sites=["open.anspire.cn", "docs.openclaw.ai"],
    top_k="10"
)

# 时间范围搜索
result = client.search("AI", from_time="2025-01-01T00:00:00")

# 新闻搜索
result = client.search_news("人工智能", count=10)

# 查看缓存统计
stats = client.get_cache_stats()
print(f"缓存: {stats['total']} 个, {stats['size_mb']} MB")
```

## 已知限制

| 限制 | Anspire | Brave |
|------|---------|-------|
| 查询字符限制 | 64 字符 | 无 |
| 最大结果数 | 50 条 | 20 条 |
| 多站搜索 | ✅ 支持（最多 20 站） | ❌ 不支持 |
| 中文新闻搜索 | ✅ 稳定 | ✅ 已修复（使用 zh-hans） |
| 时间范围 | ✅ 稳定 | ✅ 稳定 |

## 测试状态

- ✅ Anspire: 9/9 测试通过
- ✅ Brave: 4/4 测试通过
- ✅ 统一接口: 所有引擎正常工作

## 技术亮点

### 1. 缓存优化

避免重复请求，提升响应速度：

```python
from src.utils.search_cache import SearchCache

cache = SearchCache(cache_dir="/path/to/cache", ttl=86400)  # 24小时
cache_key = cache.generate_key(query, params)

if cached := cache.get(cache_key):
    return cached

result = api_call(query, params)
cache.set(cache_key, result, ttl=3600)
```

### 2. 意图识别

基于规则和模式匹配的意图识别：

```python
from src.utils.search_intent import SearchIntentAnalyzer

analyzer = SearchIntentAnalyzer()

# 站内搜索
analysis = analyzer.analyze("site:github.com openclaw")
# IntentType.SITE_SEARCH, engine="anspire"

# 时间范围
analysis = analyzer.analyze("人工智能 最近一周")
# IntentType.TIME_RANGE, engine="anspire"

# 技术搜索
analysis = analyzer.analyze("Python API 设计模式")
# IntentType.TECHNICAL, engine="anspire"
```

### 3. 时间格式修复

Anspire API 要求 ISO 8601 格式（带 T 分隔符）：

```python
# ❌ 错误
from_time="2025-01-01 00:00:00"  # 空格分隔 → 500 错误

# ✅ 正确
from_time="2025-01-01T00:00:00"  # T 分隔 → 正常
```

### 4. Brave 语言参数修复

Brave API 使用 ISO 语言代码：

```python
# ❌ 错误
search_lang="zh-CN"  # 422 错误

# ✅ 正确
search_lang="zh-hans"  # 简体中文
search_lang="zh-hant"  # 繁体中文
```

## 历史版本

### v2 - API 聚合引擎

集成了 5 个搜索源：
- GitHub API
- Hacker News API
- Reddit API
- Stack Overflow API
- DuckDuckGo HTML

详见历史文档。

### v1 - 浏览器自动化

使用 Playwright 自动化浏览器搜索：
- Google Search
- Bing Search
- DuckDuckGo Search

受反爬虫限制，部分方案不可用。

## 贡献者
Sisyphus - AI 助手

## 许可证
MIT
