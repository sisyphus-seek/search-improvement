#!/usr/bin/env python3
"""
快速搜索测试脚本
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 设置环境变量（从 credentials 读取）
os.environ['ANSPIRE_API_KEY'] = 'sk-3QUA7sEt5Jy0nBwFZvQb9J8xK2Lm4Np6Rq8St0Uv2Wx4Yz6A'
os.environ['BRAVE_API_KEY'] = 'BSAHF5MCS2x8'

from unified_search import search

def main():
    query = "如何使用 AI 在 polymarket 上交易"
    print(f"🔍 搜索查询：{query}\n")
    print("=" * 80)
    
    result = search(query, verbose=True)
    
    print(f"\n✅ 使用引擎：{result['engine']}")
    print(f"📊 结果数量：{len(result['results'])}\n")
    
    if not result['results']:
        print("❌ 未找到结果")
        return
    
    print("搜索结果:\n")
    for i, r in enumerate(result['results'][:8], 1):
        print(f"{i}. **{r.get('title', '无标题')}**")
        print(f"   链接：{r.get('url', '无链接')}")
        snippet = r.get('snippet', r.get('description', ''))
        if snippet:
            print(f"   摘要：{snippet[:200]}...")
        print()

if __name__ == '__main__':
    main()
