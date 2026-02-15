# Search Improvement Project

优化网络检索能力的实验项目。

## 目标
通过持续迭代改进搜索能力，解决以下问题：
- 传统搜索引擎 API 缺失
- 浏览器自动化被反爬虫拦截
- 第三方爬虫库选择器失效

## 当前方案 (v2)

### 统一搜索引擎 `unified_search_v2.py`

集成了 5 个搜索源，智能选择最佳源：

| 搜索源 | 用途 | 状态 | 成功率 |
|--------|------|------|--------|
| GitHub API | 代码仓库搜索 | ✅ 可用 | 100% |
| Hacker News API | 科技新闻 | ✅ 可用 | 100% |
| Reddit API | 社区讨论 | ✅ 可用 | 100% |
| Stack Overflow API | 技术问答 | ✅ 可用 | 100% |
| DuckDuckGo HTML | 通用搜索 | ✅ 可用 | 100% |

### 核心特性

- **智能查询类型检测**：自动识别 code/news/general 类型
- **自动源选择**：根据查询类型和成功率动态选择搜索源
- **成功率追踪**：实时记录各源的成功/失败率，自动降级
- **去重合并**：自动合并不同源的搜索结果并去重
- **Reddit 反爬虫修复**：通过添加浏览器头部绕过限制

### 使用方式

```python
from unified_search_v2 import UnifiedSearchEngine

engine = UnifiedSearchEngine()

# 自动检测类型并搜索
results = engine.search("python async await", limit=10)

# 指定搜索源
results = engine.search("AI agents", preferred_source="Hacker News", limit=5)

# 指定查询类型
results = engine.search("React hooks", query_type="code", limit=10)

# 查看搜索源状态
status = engine.get_status()
```

## 项目结构

```
.
├── unified_search_v2.py          # 统一搜索引擎核心
├── unified_search.py             # 旧版本（已弃用）
├── demo_search.py                # 演示脚本
├── validate_search_improvements.py  # 验证脚本
├── trend_research.py             # 趋势研究脚本
├── trend_search_simple.py        # 简化趋势搜索
├── COMPLETION_REPORT.md          # 完成报告
├── SEARCH_REPORT.md              # 搜索报告
├── REDDIT_FIXED.md               # Reddit 修复说明
└── README.md                     # 本文件
```

## 验证结果

所有搜索源经过完整验证：

```bash
python validate_search_improvements.py
```

验证报告见 `COMPLETION_REPORT.md` 和 `SEARCH_REPORT.md`

## 贡献者
Sisyphus - AI 助手

## 许可证
MIT
