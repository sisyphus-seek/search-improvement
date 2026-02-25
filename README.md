# 🔍 Prometheus Search — 智能搜索能力

**让 AI 智能体拥有完整的网络搜索能力**

本项目为 AI 智能体（如 Prometheus）提供统一的搜索接口，支持多个搜索引擎、智能缓存、意图识别。无需 API Key 配置，开箱即用。

---

## 📖 目录

- [快速开始](#-快速开始)
- [CLI 使用](#-命令行使用)
- [Python API](#-python-api)
- [搜索引擎](#-搜索引擎)
- [高级功能](#-高级功能)
- [项目结构](#-项目结构)
- [常见问题](#-常见问题)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd search-improvement
pip install -r requirements.txt
```

### 2. 配置 API Keys（可选）

API Keys 已预配置在 `credentials/` 目录，**无需手动设置**。如需更新：

```bash
# Anspire API Key
echo "your_api_key" > ../credentials/anspire_api_key.txt

# Brave API Key
echo "your_api_key" > ../credentials/brave_api_key.txt
```

### 3. 测试搜索

```bash
# 基础搜索
python3 prometheus_search.py "人工智能最新进展"

# 使用 Brave 引擎
python3 prometheus_search.py "Python bug" -e brave

# 站内搜索
python3 prometheus_search.py "openclaw" -s github.com

# 新闻搜索
python3 prometheus_search.py "AI" -n

# 输出原始 JSON
python3 prometheus_search.py "Rust" --raw
```

---

## 💻 命令行使用

### 完整参数

```bash
python3 prometheus_search.py <查询> [选项]

选项:
  -e, --engine      搜索引擎：anspire(默认) | brave | auto
  -c, --count       返回结果数量（默认：10）
  -s, --insite      站内搜索域名（如：github.com）
  --from-time       起始时间（ISO 8601 格式）
  --to-time         结束时间（ISO 8601 格式）
  -n, --news        新闻搜索模式
  --raw             输出原始 JSON
  -v, --verbose     显示详细过程
  -h, --help        显示帮助
```

### 使用示例

```bash
# 基础搜索（Anspire 引擎，10 条结果）
python3 prometheus_search.py "AI 最新进展"

# 指定 Brave 引擎
python3 prometheus_search.py "Python bug" -e brave -c 20

# 站内搜索（GitHub）
python3 prometheus_search.py "openclaw" -s github.com

# 多站搜索（用逗号分隔）
python3 prometheus_search.py "API 设计" -s "github.com,docs.openclaw.ai"

# 时间范围搜索
python3 prometheus_search.py "Rust" --from-time "2025-01-01T00:00:00"

# 新闻搜索（最近 7 天）
python3 prometheus_search.py "人工智能" -n

# 调试模式（显示意图分析、缓存命中）
python3 prometheus_search.py "技术查询" -v

# 获取 JSON 结果（用于程序处理）
python3 prometheus_search.py "查询" --raw > results.json
```

---

## 🐍 Python API

### 方式一：CLI 模块调用（推荐）

```python
from prometheus_search import search, format_results

# 执行搜索
result = search(
    query="人工智能",
    engine="anspire",  # 或 "brave"
    count=10,
    insite="github.com",  # 可选：站内搜索
    news=False
)

# 格式化输出
print(format_results(result, "anspire"))

# 或获取原始数据
import json
print(json.dumps(result, ensure_ascii=False, indent=2))
```

### 方式二：统一搜索客户端

```python
from src.unified_search import UnifiedSearchClient, SearchEngine

# 初始化（自动从环境变量加载 API Key）
client = UnifiedSearchClient()

# 基础搜索
result = client.search("人工智能", count=10)

# 指定引擎
result = client.search("Python bug", engine=SearchEngine.BRAVE, count=20)

# 时间范围搜索
result = client.search(
    "Rust",
    from_time="2025-01-01T00:00:00",
    to_time="2025-12-31T23:59:59"
)

# 新闻搜索
result = client.search_news("AI", count=10)

# 意图分析
intent = client.analyze_intent("site:github.com openclaw")
print(f"意图类型：{intent['type']}, 推荐引擎：{intent['engine']}")

# 缓存统计
stats = client.get_cache_stats()
print(f"缓存：{stats['total']} 个，{stats['size_mb']} MB")
```

### 方式三：直接使用引擎

```python
# Anspire 引擎
from src.engines.anspire_search import AnspireSearchAgent

agent = AnspireSearchAgent(enable_cache=True, enable_intent=True)
result = agent.search(
    query="API 设计",
    top_k=10,
    insite="github.com",
    from_time="2025-01-01T00:00:00"
)

# Brave 引擎
from src.engines.brave_search import BraveSearchClient

client = BraveSearchClient()
result = client.search(query="Python", count=10)
result = client.search_news(query="AI", count=10, freshness="pw")
```

---

## 🔎 搜索引擎

### 引擎对比

| 特性 | Anspire | Brave |
|------|---------|-------|
| **优先级** | 1（默认） | 2（回退） |
| **AI 增强** | ✅ 支持 | ❌ 不支持 |
| **站内搜索** | ✅ 最多 20 站 | ❌ 不支持 |
| **时间范围** | ✅ 精确（ISO 8601） | ✅ 模糊（freshness） |
| **新闻搜索** | ✅ 支持 | ✅ 支持 |
| **最大结果** | 50 条 | 20 条 |
| **查询限制** | ≤64 字符 | 无限制 |
| **中文支持** | ✅ 优秀 | ✅ 良好 |

### 引擎选择建议

| 场景 | 推荐引擎 | 理由 |
|------|---------|------|
| 技术搜索 | Anspire | AI 增强，理解代码/API 查询 |
| 站内搜索 | Anspire | 支持多站，语法灵活 |
| 时间范围 | Anspire | 精确时间控制 |
| 新闻搜索 | Anspire → Brave | 两者都支持，Anspire 优先 |
| 长查询 | Brave | 无字符限制 |
| 快速响应 | Brave | 通常更快 |

---

## ⚡ 高级功能

### 1. 搜索结果缓存

- **位置**: `~/.workspace/cache/search/`
- **TTL**: 24 小时
- **Key**: MD5(查询 + 参数)
- **自动清理**: 过期自动删除

```python
# 查看缓存统计
stats = client.get_cache_stats()
print(f"缓存命中：{stats['hits']} 次，节省：{stats['saved_requests']} 次请求")
```

### 2. 搜索意图识别

支持 6 种意图类型，自动选择最佳引擎：

| 意图类型 | 识别特征 | 推荐引擎 |
|---------|---------|---------|
| 站内搜索 | `site:domain` | Anspire |
| 多站搜索 | 多个 `site:` | Anspire |
| 时间范围 | `from:`, `最近`, `本周` | Anspire |
| 技术搜索 | API, Python, 代码相关 | Anspire |
| 新闻搜索 | 新闻，最新，发布 | Anspire → Brave |
| 通用搜索 | 其他查询 | Anspire → Brave |

```python
# 手动分析意图
intent = client.analyze_intent("site:github.com openclaw")
# 返回：{"type": "SITE_SEARCH", "engine": "anspire", ...}
```

### 3. 时间格式

**Anspire 格式**（ISO 8601）：
```
2025-01-01T00:00:00  # ✅ 正确（T 分隔）
2025-01-01 00:00:00  # ❌ 错误（空格分隔）
```

**Brave 格式**（freshness）：
```
p1d  # 最近 1 天
pw   # 最近 1 周
pm   # 最近 1 月
py   # 最近 1 年
```

### 4. 错误处理

```python
result = search(query="测试")

if "error" in result:
    print(f"搜索失败：{result['error']}")
else:
    print(f"找到 {len(result.get('results', []))} 个结果")
```

---

## 📁 项目结构

```
search-improvement/
├── prometheus_search.py        # 唯一 CLI 入口
├── src/
│   ├── unified_search.py       # 统一搜索客户端
│   ├── engines/
│   │   ├── anspire_search.py   # Anspire 引擎
│   │   └── brave_search.py     # Brave 引擎
│   ├── utils/
│   │   ├── search_cache.py     # 缓存模块
│   │   └── search_intent.py    # 意图识别模块
│   └── tests/
│       ├── test_anspire.py     # Anspire 测试
│       ├── test_brave.py       # Brave 测试
│       ├── test_prometheus.py  # CLI 测试
│       └── test_search_enhancements.py
├── archive/                    # 历史代码归档
├── requirements.txt            # Python 依赖
├── .gitignore
└── README.md                   # 本文档
```

---

## ❓ 常见问题

### Q: 为什么搜索失败？

**A:** 检查以下几点：
1. API Key 是否正确配置（`credentials/` 目录）
2. 网络连接是否正常
3. 查询是否超过 64 字符（Anspire 限制）
4. 使用 `-v` 参数查看详细错误

### Q: 如何选择搜索引擎？

**A:** 
- 默认使用 Anspire（功能更全）
- 长查询用 Brave（无字符限制）
- 需要多站搜索用 Anspire

### Q: 缓存如何清理？

**A:** 缓存自动管理，24 小时后自动过期。手动清理：
```bash
rm -rf ~/.workspace/cache/search/*
```

### Q: 如何贡献代码？

**A:** 
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/xxx`)
3. 提交修改 (`git commit -m 'feat: 添加 xxx'`)
4. 推送到远程 (`git push origin feature/xxx`)
5. 创建 Pull Request

---

## 📝 更新日志

### v3.0 (当前版本)
- ✅ 双引擎支持（Anspire + Brave）
- ✅ 统一搜索接口
- ✅ 24 小时缓存
- ✅ 意图识别（6 种类型）
- ✅ CLI 和 Python API

### v2.0
- API 聚合引擎（GitHub/HN/Reddit/StackOverflow）

### v1.0
- 浏览器自动化（Playwright）

---

## 📄 许可证

MIT License

---

**🦀 让搜索变得简单**
