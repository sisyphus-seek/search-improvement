#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspace/projects/search-improvement')

from unified_search_v2 import UnifiedSearchEngine

engine = UnifiedSearchEngine()

print("优化后的检索能力验证")
print("=" * 80)

# 测试 1: 代码查询
print("\n测试 1: 代码查询 'python asyncio'")
results = engine.search("python asyncio", limit=3)
print(f"找到 {len(results)} 个结果")
for r in results:
    print(f"  [{r.source}] {r.title}")

# 测试 2: 新闻查询
print("\n测试 2: 新闻查询 'AI release'")
results = engine.search("AI release", limit=3)
print(f"找到 {len(results)} 个结果")
for r in results:
    print(f"  [{r.source}] {r.title}")

# 测试 3: 技术话题
print("\n测试 3: 技术话题 'RAG system'")
results = engine.search("RAG system", limit=3)
print(f"找到 {len(results)} 个结果")
for r in results:
    print(f"  [{r.source}] {r.title}")

# 测试 4: 通用查询
print("\n测试 4: 通用查询 'best tutorial'")
results = engine.search("best tutorial", limit=3)
print(f"找到 {len(results)} 个结果")
for r in results:
    print(f"  [{r.source}] {r.title}")

# 测试 5: 社区讨论
print("\n测试 5: 社区讨论 'machine learning career'")
results = engine.search("machine learning career", limit=3)
print(f"找到 {len(results)} 个结果")
for r in results:
    print(f"  [{r.source}] {r.title}")

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

# 计算整体成功率
total_success = sum(m['success_count'] for m in status.values())
total_failure = sum(m['failure_count'] for m in status.values())
overall_rate = total_success / (total_success + total_failure) if (total_success + total_failure) > 0 else 0

print(f"\n整体成功率: {overall_rate:.2%}")
print("=" * 80)
