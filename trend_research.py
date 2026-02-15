#!/usr/bin/env python3
"""
技术趋势调研 - 2026年2月
使用优化后的搜索能力
"""
import sys
sys.path.insert(0, '/workspace/projects/search-improvement')

from unified_search_v2 import UnifiedSearchEngine

engine = UnifiedSearchEngine()

print("=" * 80)
print("2026年初技术趋势调研")
print("=" * 80)

trends = [
    ("RAG retrieval augmented generation", "检索增强生成"),
    ("MCP Model Context Protocol", "模型上下文协议"),
    ("Agentic AI framework", "AI Agent 框架"),
    ("WebGPU browser", "WebGPU 浏览器"),
    ("Small Language Models SLM", "小型语言模型"),
]

for query, topic_zh in trends:
    print(f"\n{'=' * 80}")
    print(f"趋势：{topic_zh}")
    print(f"查询：{query}")
    print('=' * 80)

    results = engine.search(query, limit=5)

    print(f"\n找到 {len(results)} 个结果：\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r.source}] {r.title}")
        print(f"   {r.url}")
        if r.metadata and r.metadata:
            # 格式化显示元数据
            meta_parts = []
            for key, value in r.metadata.items():
                if value and str(value) != "":
                    meta_parts.append(f"{key}: {value}")
            if meta_parts:
                print(f"   {', '.join(meta_parts)}")
        print()

# 显示搜索源状态
print("\n" + "=" * 80)
print("搜索源状态汇总")
print("=" * 80)
status = engine.get_status()
for source_name, metrics in status.items():
    print(f"\n{source_name}:")
    print(f"  成功率: {metrics['success_rate']}")
    print(f"  成功: {metrics['success_count']}")
    print(f"  失败: {metrics['failure_count']}")

print("\n" + "=" * 80)
