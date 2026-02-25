#!/usr/bin/env python3
"""
使用优化后的检索能力进行实际搜索演示
"""
import sys
sys.path.insert(0, '/workspace/projects/search-improvement')

from unified_search_v2 import UnifiedSearchEngine

engine = UnifiedSearchEngine()

print("=" * 80)
print("优化后的检索能力 - 实际搜索演示")
print("=" * 80)
print()

# 搜索主题：2025-2026 年前沿 AI 技术
topics = [
    ("DeepSeek R1 model", "DeepSeek R1 模型"),
    ("Claude 4 Sonnet", "Claude 4 Sonnet"),
    ("GPT-5 rumors", "GPT-5 传闻"),
    ("AI agents 2026", "AI Agents 2026"),
]

for query, topic_zh in topics:
    print(f"\n{'─' * 80}")
    print(f"📌 主题: {topic_zh}")
    print(f"🔍 查询: {query}")
    print('─' * 80)

    results = engine.search(query, limit=3)

    if not results:
        print("❌ 未找到结果")
        continue

    print(f"\n✅ 找到 {len(results)} 个结果:\n")

    for i, r in enumerate(results, 1):
        print(f"{i}. {r.title}")
        print(f"   来源: {r.source}")
        print(f"   链接: {r.url}")

        # 显示元数据
        if r.metadata:
            meta_lines = []
            if 'stars' in r.metadata and r.metadata['stars']:
                meta_lines.append(f"⭐ {r.metadata['stars']} stars")
            if 'points' in r.metadata and r.metadata['points']:
                meta_lines.append(f"👆 {r.metadata['points']} points")
            if 'score' in r.metadata and r.metadata['score']:
                meta_lines.append(f"👍 {r.metadata['score']} score")
            if meta_lines:
                print(f"   指标: {', '.join(meta_lines)}")

        print()

# 显示统计
print("=" * 80)
print("搜索统计")
print("=" * 80)
status = engine.get_status()
total_success = sum(m['success_count'] for m in status.values())
total_failure = sum(m['failure_count'] for m in status.values())
overall_rate = total_success / (total_success + total_failure) if (total_success + total_failure) > 0 else 0

print(f"\n📊 整体成功率: {overall_rate:.1%}")
print(f"📊 成功搜索: {total_success}")
print(f"📊 失败搜索: {total_failure}")
print(f"📊 可用搜索源: {len([s for s, m in status.items() if float(str(m['success_rate']).rstrip('%')) > 0])}/5")
print()

print("搜索源详情:")
for source_name, metrics in status.items():
    if metrics['success_count'] > 0 or metrics['failure_count'] > 0:
        rate_str = metrics['success_rate']
        print(f"  • {source_name}: {rate_str}")

print("\n" + "=" * 80)
