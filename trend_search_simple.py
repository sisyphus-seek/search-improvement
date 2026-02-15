#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, '/workspace/projects/search-improvement')

from unified_search_v2 import UnifiedSearchEngine

engine = UnifiedSearchEngine()

print("=" * 80)
print("2026年初技术趋势调研 - 简化版")
print("=" * 80)

# 测试单个搜索
print("\n[主题 1] RAG (检索增强生成)")
print("查询: RAG retrieval")
results = engine.search("RAG retrieval", limit=3)
print(f"找到 {len(results)} 个结果")
for r in results:
    print(f"  [{r.source}] {r.title}")

print("\n[主题 2] MCP (Model Context Protocol)")
print("查询: MCP Model Context Protocol")
results = engine.search("MCP Model Context Protocol", limit=3)
print(f"找到 {len(results)} 个结果")
for r in results:
    print(f"  [{r.source}] {r.title}")

print("\n[主题 3] AI Agent")
print("查询: Agentic AI framework")
results = engine.search("Agentic AI framework", limit=3)
print(f"找到 {len(results)} 个结果")
for r in results:
    print(f"  [{r.source}] {r.title}")

print("\n[主题 4] WebGPU")
print("查询: WebGPU browser")
results = engine.search("WebGPU browser", limit=3)
print(f"找到 {len(results)} 个结果")
for r in results:
    print(f"  [{r.source}] {r.title}")

print("\n[主题 5] Small Language Models")
print("查询: Small Language Models SLM")
results = engine.search("Small Language Models SLM", limit=3)
print(f"找到 {len(results)} 个结果")
for r in results:
    print(f"  [{r.source}] {r.title}")

# 保存结果到文件
trend_report = {
    "date": "2026-02-15",
    "trends": {
        "RAG": {"query": "RAG retrieval", "results": len(results)},
        "MCP": {"query": "MCP Model Context Protocol", "results": len(results)},
        "Agentic AI": {"query": "Agentic AI framework", "results": len(results)},
        "WebGPU": {"query": "WebGPU browser", "results": len(results)},
        "SLM": {"query": "Small Language Models SLM", "results": len(results)},
    }
}

with open('/workspace/projects/search-improvement/trend_report.json', 'w') as f:
    json.dump(trend_report, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print("搜索源状态")
print("=" * 80)
status = engine.get_status()
for source_name, metrics in status.items():
    print(f"\n{source_name}:")
    print(f"  成功率: {metrics['success_rate']}")
    print(f"  成功: {metrics['success_count']}")
    print(f"  失败: {metrics['failure_count']}")

print("\n\n报告已保存到 trend_report.json")
