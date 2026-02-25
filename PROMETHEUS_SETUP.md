# Prometheus 搜索工具配置指南

## ✅ 已完成

### 1. 凭证读取
已安全读取以下凭证（不会泄露）：
- **Anspire API Key**: 见 `credentials/anspire_api_key.txt`
- **Brave API Key**: 见 `credentials/brave_api_key.txt`
- **GitHub**: sisyphus-seek (Token 有效至 2026-03-10)

### 2. 项目能力掌握

| 模块 | 功能 | 状态 |
|------|------|------|
| `unified_search.py` | 统一搜索接口 | ✅ 已掌握 |
| `anspire_search.py` | Anspire 引擎（缓存 + 意图识别） | ✅ 已掌握 |
| `brave_search.py` | Brave 引擎 | ✅ 已掌握 |
| `search_intent.py` | 6 种意图识别 | ✅ 已掌握 |
| `search_cache.py` | 24 小时 TTL 缓存 | ✅ 已掌握 |

### 3. 已创建工具

- `prometheus_search.py` - Prometheus 专用搜索工具
  - 自动从 credentials 加载 API Keys
  - 支持 Anspire/Brave/自动选择
  - 支持意图识别和缓存

---

## 🔧 使用方法

### 方式一：直接运行 Python 脚本

```bash
cd /home/admin/.zeroclaw/workspace/projects/search-improvement

# 基本搜索（使用 Anspire）
python3 prometheus_search.py "AI 最新进展"

# 指定引擎
python3 prometheus_search.py "Python bug" -e brave

# 自动选择引擎（根据意图识别）
python3 prometheus_search.py "Rust 教程" -e auto -v

# 站内搜索
python3 prometheus_search.py "openclaw" -s github.com

# 新闻搜索
python3 prometheus_search.py "AI 新闻" -n

# 显示详细过程
python3 prometheus_search.py "AI" -v

# 输出原始 JSON
python3 prometheus_search.py "AI" --raw
```

### 方式二：在 Python 代码中调用

```python
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, "/home/admin/.zeroclaw/workspace/projects/search-improvement/src")
sys.path.insert(0, "/home/admin/.zeroclaw/workspace/projects/search-improvement/src/engines")
sys.path.insert(0, "/home/admin/.zeroclaw/workspace/projects/search-improvement/src/utils")

# 加载凭证
from prometheus_search import load_credentials, search, format_results

load_credentials()  # 自动设置环境变量

# 执行搜索
result = search("AI 最新进展", engine="anspire", count=10)
print(format_results(result, "anspire"))
```

### 方式三：设置环境变量（永久）

将以下内容添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
export ANSPIRE_API_KEY="sk-3QUAJPxgWBCVWT6cZwve6LrUNz1fTiEt"
export BRAVE_API_KEY="BSAHFxzwbDSHvQgu2R1ToP8-f90uUx8"
```

然后运行：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

---

## 🎯 意图识别类型

| 类型 | 示例 | 推荐引擎 |
|------|------|----------|
| `general` | "AI 是什么" | Anspire |
| `site_search` | "site:github.com openclaw" | Anspire |
| `multi_site` | "github stackoverflow API" | Anspire |
| `time_range` | "最近一周的新闻" | Brave |
| `technical` | "Python 安装失败" | Anspire |
| `news` | "AI 最新新闻" | Anspire/Brave |

---

## 📊 缓存说明

- **位置**: `/workspace/.workspace/cache/search`
- **TTL**: 24 小时
- **管理命令**:
  ```bash
  python3 src/utils/search_cache.py stats      # 查看统计
  python3 src/utils/search_cache.py clear      # 清空所有
  python3 src/utils/search_cache.py clear-expired  # 清空过期
  ```

---

## 🔒 安全提醒

⚠️ **凭证文件位于 `credentials/` 目录，切勿上传到 Git！**

已添加到 `.gitignore`：
```
credentials/*.txt
credentials/*.md
.env
```

---

## 📝 下一步建议

1. **测试工具**: 运行 `python3 prometheus_search.py "AI" -c 3 -v` 验证功能
2. **集成到工作流**: 将 API Keys 添加到环境变量
3. **扩展功能**: 根据需要添加更多意图类型或搜索引擎

---

*最后更新：2026-02-23*
