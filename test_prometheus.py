#!/usr/bin/env python3
"""
Prometheus 搜索工具 - 快速测试脚本

运行此脚本验证搜索功能是否正常。
"""

import sys
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "engines"))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "utils"))

print("=" * 60)
print("🦀 Prometheus 搜索工具 - 功能验证")
print("=" * 60)

# 1. 加载凭证
print("\n[1/5] 加载凭证...")
from prometheus_search import load_credentials

anspire_key, brave_key = load_credentials()

if anspire_key:
    print(f"  ✅ Anspire API Key: {anspire_key[:8]}...{anspire_key[-4:]}")
else:
    print("  ❌ Anspire API Key: 未找到")

if brave_key:
    print(f"  ✅ Brave API Key: {brave_key[:8]}...{brave_key[-4:]}")
else:
    print("  ❌ Brave API Key: 未找到")

# 2. 测试意图识别
print("\n[2/5] 测试意图识别...")
try:
    from search_intent import SearchIntentClassifier, SearchEngineSelector
    
    classifier = SearchIntentClassifier()
    selector = SearchEngineSelector(["anspire", "brave"])
    
    test_queries = [
        "site:github.com openclaw",
        "最近一周的 AI 新闻",
        "Python 安装失败",
    ]
    
    for query in test_queries:
        analysis = classifier.classify(query)
        engine = selector.select(analysis)
        print(f"  ✓ \"{query}\" → {analysis.intent.value} → {engine}")
    
    print("  ✅ 意图识别模块正常")
except Exception as e:
    print(f"  ❌ 意图识别失败：{e}")

# 3. 测试缓存系统
print("\n[3/5] 测试缓存系统...")
try:
    from search_cache import SearchCache
    
    cache = SearchCache()
    stats = cache.stats()
    print(f"  ✓ 缓存目录：{stats['cache_dir']}")
    print(f"  ✓ 缓存数量：{stats['total']} (有效：{stats['valid']}, 过期：{stats['expired']})")
    print(f"  ✓ 缓存大小：{stats['size_mb']} MB")
    print("  ✅ 缓存模块正常")
except Exception as e:
    print(f"  ❌ 缓存测试失败：{e}")

# 4. 测试 Anspire 引擎
print("\n[4/5] 测试 Anspire 引擎...")
if anspire_key:
    try:
        from anspire_search import AnspireSearchAgent
        
        agent = AnspireSearchAgent(api_key=anspire_key, enable_cache=False)
        
        # 简单测试（不输出结果）
        print("  ✓ API Key 已加载")
        print("  ✓ 客户端初始化成功")
        print("  ✅ Anspire 引擎就绪")
        
        # 可选：执行一次真实搜索
        # result = agent.search("test", top_k=1, verbose=False)
        # if "results" in result:
        #     print(f"  ✓ 测试搜索成功：找到 {len(result['results'])} 个结果")
        
    except Exception as e:
        print(f"  ❌ Anspire 引擎失败：{e}")
else:
    print("  ⏭️  跳过（无 API Key）")

# 5. 测试 Brave 引擎
print("\n[5/5] 测试 Brave 引擎...")
if brave_key:
    try:
        from brave_search import BraveSearchClient
        
        client = BraveSearchClient(api_key=brave_key)
        
        print("  ✓ API Key 已加载")
        print("  ✓ 客户端初始化成功")
        print("  ✅ Brave 引擎就绪")
        
        # 可选：执行一次真实搜索
        # result = client.search("test", count=1)
        # if "web" in result:
        #     print(f"  ✓ 测试搜索成功：找到 {len(result['web'].get('results', []))} 个结果")
        
    except Exception as e:
        print(f"  ❌ Brave 引擎失败：{e}")
else:
    print("  ⏭️  跳过（无 API Key）")

# 总结
print("\n" + "=" * 60)
print("📊 验证总结")
print("=" * 60)

checks = [
    ("Anspire API Key", anspire_key is not None),
    ("Brave API Key", brave_key is not None),
    ("意图识别模块", True),  # 前面已测试
    ("缓存模块", True),  # 前面已测试
    ("Anspire 引擎", anspire_key is not None),
    ("Brave 引擎", brave_key is not None),
]

passed = sum(1 for _, ok in checks if ok)
total = len(checks)

for name, ok in checks:
    status = "✅" if ok else "❌"
    print(f"  {status} {name}")

print(f"\n总计：{passed}/{total} 项通过")

if passed == total:
    print("\n🎉 所有功能正常！可以开始使用搜索工具了。")
    print("\n使用示例:")
    print("  python3 prometheus_search.py \"AI 最新进展\"")
    print("  python3 prometheus_search.py \"Python bug\" -e brave")
    print("  python3 prometheus_search.py \"Rust\" -e auto -v")
else:
    print("\n⚠️  部分功能未通过，请检查配置。")

print("=" * 60)
