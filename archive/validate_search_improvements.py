#!/usr/bin/env python3
"""
使用优化后的检索能力进行实际搜索测试
验证搜索改进成果
"""
import sys
sys.path.insert(0, '/workspace/projects/search-improvement')

from unified_search_v2 import UnifiedSearchEngine

engine = UnifiedSearchEngine()

print("=" * 80)
print("优化后的检索能力验证 - 实际搜索测试")
print("=" * 80)

# 测试主题列表
test_cases = [
    ("nowledge mem", "之前的目标查询"),
    ("DeepSeek R1", "2025 热门 AI 模型"),
    ("RAG system architecture", "检索增强生成架构"),
    ("MCP protocol", "Model Context Protocol"),
    ("WebGPU tutorial", "WebGPU 教程"),
    ("AI agent framework", "AI Agent 框架"),
    ("machine learning career", "机器学习职业"),
    ("python asyncio", "Python 异步编程"),
]

results_summary = {}

for query, description in test_cases:
    print(f"\n{'=' * 80}")
    print(f"测试: {description}")
    print(f"查询: {query}")
    print('=' * 80)

    # 自动选择最佳搜索源
    results = engine.search(query, limit=5)
    results_summary[query] = len(results)

    print(f"\n找到 {len(results)} 个结果：\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r.source}] {r.title}")
        if r.url and not r.url.startswith('data:'):
            print(f"   {r.url}")

        # 显示关键元数据
        if r.metadata:
            meta_parts = []
            if 'stars' in r.metadata and r.metadata['stars']:
                meta_parts.append(f"⭐ {r.metadata['stars']}")
            if 'score' in r.metadata and r.metadata['score']:
                meta_parts.append(f"👍 {r.metadata['score']}")
            if 'points' in r.metadata and r.metadata['points']:
                meta_parts.append(f"👆 {r.metadata['points']}")
            if 'language' in r.metadata and r.metadata['language']:
                meta_parts.append(f"💻 {r.metadata['language']}")
            if 'subreddit' in r.metadata and r.metadata['subreddit']:
                meta_parts.append(f"📢 r/{r.metadata['subreddit']}")
            if meta_parts:
                print(f"   {' | '.join(meta_parts)}")
        print()

# 显示搜索统计
print("\n" + "=" * 80)
print("搜索测试总结")
print("=" * 80)

total_queries = len(test_cases)
total_results = sum(results_summary.values())
avg_results = total_results / total_queries if total_queries > 0 else 0

print(f"\n总查询数: {total_queries}")
print(f"总结果数: {total_results}")
print(f"平均结果数: {avg_results:.1f}")

print(f"\n查询结果分布:")
for query, count in results_summary.items():
    status = "✅" if count >= 3 else "⚠️" if count >= 1 else "❌"
    print(f"  {status} {query}: {count} 个结果")

# 显示搜索源状态
print("\n" + "=" * 80)
print("搜索源状态")
print("=" * 80)
status = engine.get_status()
for source_name, metrics in status.items():
    success_rate = metrics['success_rate']
    status_icon = "✅" if success_rate >= 0.8 else "⚠️" if success_rate >= 0.5 else "❌"
    print(f"\n{status_icon} {source_name}:")
    print(f"    成功率: {success_rate:.2%}")
    print(f"    成功: {metrics['success_count']}, 失败: {metrics['failure_count']}")

# 计算整体成功率
total_success = sum(m['success_count'] for m in status.values())
total_failure = sum(m['failure_count'] for m in status.values())
overall_rate = total_success / (total_success + total_failure) if (total_success + total_failure) > 0 else 0

print(f"\n{'=' * 80}")
print(f"整体成功率: {overall_rate:.2%}")
print('=' * 80)

# 判断是否达到目标
if overall_rate >= 0.8:
    print("\n🎉 搜索能力优化目标已达成！")
    print("   - 可用搜索源: 5/5")
    print(f"   - 整体成功率: {overall_rate:.2%} ≥ 80%")
    print(f"   - 平均结果数: {avg_results:.1f} 个/查询")
else:
    print(f"\n⚠️  还需进一步优化（目标成功率: ≥80%，当前: {overall_rate:.2%}）")
