#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspace/projects/search-improvement')

from unified_search_v2 import UnifiedSearchEngine

engine = UnifiedSearchEngine()

print("=" * 80)
print("测试修复后的 Reddit 搜索")
print("=" * 80)

print("\n搜索 'machine learning'：")
results = engine.search("machine learning", preferred_source="Reddit", limit=5)
print(f"找到 {len(results)} 个结果：\n")

for i, r in enumerate(results, 1):
    print(f"{i}. {r.title}")
    print(f"   [{r.source}]")
    print(f"   {r.url}")
    if r.metadata and r.metadata:
        print(f"   Score: {r.metadata.get('score', 0)}, Subreddit: {r.metadata.get('subreddit', 'N/A')}")
    print()

# 测试其他查询
print("\n搜索 'nowledge mem'：")
results = engine.search("nowledge mem", preferred_source="Reddit", limit=3)
print(f"找到 {len(results)} 个结果：\n")
for i, r in enumerate(results, 1):
    print(f"{i}. {r.title}")
    print(f"   {r.url}\n")

# 显示状态
print("\n" + "=" * 80)
print("搜索源状态")
print("=" * 80)
status = engine.get_status()
for source_name, metrics in status.items():
    print(f"\n{source_name}:")
    print(f"  成功率: {metrics['success_rate']}")
    print(f"  成功: {metrics['success_count']}")
    print(f"  失败: {metrics['failure_count']}")
