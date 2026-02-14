#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspace/projects/search-improvement')

from unified_search_v2 import UnifiedSearchEngine

engine = UnifiedSearchEngine()

print("=" * 60)
print("使用优化后的搜索能力 - 技术趋势调研")
print("=" * 60)

# 主题 1: DeepSeek (中国 AI 公司，2025 年初很热门)
print("\n[主题 1] 搜索 'DeepSeek R1':")
results = engine.search("DeepSeek R1", limit=5)
for r in results:
    print(f"  [{r.source}] {r.title}")

# 主题 2: MCP (Model Context Protocol，趋势技术)
print("\n[主题 2] 搜索 'MCP Model Context Protocol':")
results = engine.search("MCP Model Context Protocol", limit=5)
for r in results:
    print(f"  [{r.source}] {r.title}")

# 主题 3: WebGPU (浏览器 GPU 加速)
print("\n[主题 3] 搜索 'WebGPU browser':")
results = engine.search("WebGPU browser", limit=5)
for r in results:
    print(f"  [{r.source}] {r.title}")

# 主题 4: RAG (检索增强生成)
print("\n[主题 4] 搜索 'RAG retrieval augmented generation':")
results = engine.search("RAG retrieval augmented generation", limit=5)
for r in results:
    print(f"  [{r.source}] {r.title}")

# 显示状态
print("\n" + "=" * 60)
print("搜索源状态")
print("=" * 60)
status = engine.get_status()
for source_name, metrics in status.items():
    print(f"\n{source_name}:")
    print(f"  成功率: {metrics['success_rate']}")
    print(f"  成功: {metrics['success_count']}")
    print(f"  失败: {metrics['failure_count']}")
