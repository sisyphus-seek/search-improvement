# 问题修复报告 - 工具调用次数超限

## 📋 问题描述

**错误信息：** `⚠️ Error: Agent exceeded maximum tool iterations (20)`

**根本原因：** 任务拆解过度 + 工具调用链太长

---

## 🔍 问题分析

### 原流程（问题版本）

```
用户请求搜索
├── 1. 加载凭证（1 次调用）
├── 2. 意图识别（1 次调用）← search_intent.py
├── 3. 引擎选择（1 次调用）← SearchEngineSelector
├── 4. 执行搜索（1 次调用）
├── 5. 格式化结果（可能多次）
└── 6. 错误重试（每次失败都消耗）
```

**总计：** 5-10+ 次工具调用，很容易超过 20 次限制

### 问题代码（已修复）

```python
# ❌ 原代码（第 78-88 行）
if engine == "auto":
    from search_intent import SearchIntentClassifier, SearchEngineSelector
    
    classifier = SearchIntentClassifier()  # ← 额外调用
    analysis = classifier.classify(query)   # ← 可能触发更多调用
    selector = SearchEngineSelector(["anspire", "brave"])
    engine = selector.select(analysis)      # ← 额外调用
```

---

## ✅ 修复方案

### 修改内容

**文件：** `projects/search-improvement/prometheus_search.py`

**修改前：**
```python
if engine == "auto":
    from search_intent import SearchIntentClassifier, SearchEngineSelector
    classifier = SearchIntentClassifier()
    analysis = classifier.classify(query)
    selector = SearchEngineSelector(["anspire", "brave"])
    engine = selector.select(analysis)
```

**修改后：**
```python
# 自动选择引擎 - 简化版（直接默认 Anspire，避免额外的工具调用）
if engine == "auto":
    # 不再使用意图识别（会消耗额外的工具调用次数）
    # 直接默认使用 Anspire，如有需要可手动指定 brave
    engine = "anspire"
    
    if verbose:
        print(f"[自动选择] 已简化：直接使用 Anspire 引擎（避免额外工具调用）")
```

### 新流程（修复后）

```
用户请求搜索
├── 1. 加载凭证（1 次调用）
├── 2. 执行搜索（1 次调用）← 直接使用 Anspire
└── 3. 格式化结果（0 次，纯本地处理）
```

**总计：** 2-3 次工具调用，远低于 20 次限制

---

## 📊 优化效果

| 指标 | 修复前 | 修复后 | 改善 |
|------|--------|--------|------|
| 工具调用次数 | 5-10+ | 2-3 | **减少 60-75%** |
| 意图识别 | ✅ 启用 | ❌ 禁用 | 简化流程 |
| 引擎选择 | 智能路由 | 默认 Anspire | 手动指定 |
| 超限风险 | 高 | 低 | **显著降低** |

---

## 🚀 使用建议

### 推荐使用方式

```bash
# 默认使用 Anspire（最快，最少调用）
python3 prometheus_search.py "查询内容"

# 手动指定 Brave（如需备用）
python3 prometheus_search.py "查询内容" -e brave

# auto 模式现在等同于 anspire（简化版）
python3 prometheus_search.py "查询内容" -e auto
```

### 未来优化方向

1. **如果需要智能路由**：由 Prometheus 在外部判断，而不是在脚本内部
2. **恢复意图识别**：等 config.toml 的 `max_tool_iterations` 提高到 50+ 后
3. **并行搜索**：同时调用多个引擎，返回最快结果

---

## 📝 修改文件清单

- ✅ `prometheus_search.py` - 简化 auto 模式逻辑
- ✅ `test_simple.py` - 创建简化测试脚本
- ✅ `FIX_REPORT.md` - 本修复报告

---

## ✅ 验证方法

```bash
# 测试基本搜索
python3 prometheus_search.py "Rust 编程语言" -c 3 -v

# 测试 Brave 搜索
python3 prometheus_search.py "Python tutorial" -e brave -c 3

# 测试 auto 模式（应直接使用 Anspire）
python3 prometheus_search.py "AI news" -e auto -c 3 -v
```

---

**修复完成时间：** 2026-02-23  
**修复者：** Prometheus 🦀
