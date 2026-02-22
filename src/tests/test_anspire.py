#!/usr/bin/env python3
"""
Anspire Search Agent 测试脚本

运行前请设置环境变量：
export ANSPIRE_API_KEY="your-api-key-here"
"""

import os
import sys
import requests
from anspire_search import AnspireSearchAgent


def test_basic_search():
    """测试基本搜索"""
    print("=== 测试基本搜索 ===")
    try:
        agent = AnspireSearchAgent()
        result = agent.search("人工智能", top_k=3)

        if "results" in result:
            print(f"✓ 基本搜索成功")
            print(f"  找到 {len(result['results'])} 个结果")
            if result['results']:
                print(f"  第一个结果: {result['results'][0]['title'][:50]}...")
        else:
            print(f"✗ 搜索失败: {result.get('detail', '未知错误')}")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def test_site_search():
    """测试站内搜索"""
    print("=== 测试站内搜索 ===")
    try:
        agent = AnspireSearchAgent()
        result = agent.search("AI", insite="github.com", top_k=3)

        if "results" in result:
            print(f"✓ 站内搜索成功")
            print(f"  找到 {len(result['results'])} 个结果")
            if result['results']:
                print(f"  第一个结果: {result['results'][0]['title'][:50]}...")
        else:
            print(f"✗ 搜索失败: {result.get('detail', '未知错误')}")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def test_time_range():
    """测试时间范围搜索"""
    print("=== 测试时间范围搜索 ===")
    try:
        agent = AnspireSearchAgent()

        # 测试 ISO 8601 格式（T 分隔）
        print("  测试 ISO 8601 格式...")
        result = agent.search(
            "AI",
            from_time="2025-01-01T00:00:00",
            to_time="2025-02-01T00:00:00",
            top_k=3
        )

        if "results" in result:
            print(f"  ✓ ISO 8601 格式成功，找到 {len(result['results'])} 个结果")
        else:
            print(f"  ✗ ISO 8601 格式失败: {result.get('detail', '未知错误')}")
            return False

        # 测试仅日期格式
        print("  测试仅日期格式...")
        result2 = agent.search(
            "AI",
            from_time="2025-01-01",
            to_time="2025-02-01",
            top_k=3,
            use_cache=False
        )

        if "results" in result2:
            print(f"  ✓ 仅日期格式成功，找到 {len(result2['results'])} 个结果")
        else:
            print(f"  ✗ 仅日期格式失败: {result2.get('detail', '未知错误')}")
            return False

        print(f"✓ 时间范围搜索成功")
    except requests.HTTPError as e:
        print(f"✗ 测试失败: HTTP {e.response.status_code}")
        if e.response.text:
            print(f"  错误信息: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def test_multi_site():
    """测试多站搜索"""
    print("=== 测试多站搜索 ===")
    try:
        agent = AnspireSearchAgent()
        result = agent.search_multi_site(
            "API",
            sites=["open.anspire.cn", "docs.openclaw.ai"],
            top_k=3
        )

        if "results" in result:
            print(f"✓ 多站搜索成功")
            print(f"  找到 {len(result['results'])} 个结果")
        else:
            print(f"✗ 搜索失败: {result.get('detail', '未知错误')}")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def main():
    """运行所有测试"""
    print("Anspire Search Agent 测试\n")
    print("=" * 50)
    print()

    # 检查 API Key
    if not os.environ.get("ANSPIRE_API_KEY"):
        print("错误: 未设置 ANSPIRE_API_KEY 环境变量")
        print("\n请先获取 API Key:")
        print("  1. 访问 https://open.anspire.cn/")
        print("  2. 注册并获取免费 API Key")
        print("  3. 运行: export ANSPIRE_API_KEY='your-key-here'")
        sys.exit(1)

    # 运行测试
    tests = [
        test_basic_search,
        test_site_search,
        test_time_range,
        test_multi_site
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}\n")
            failed += 1

    # 总结
    print("=" * 50)
    print(f"\n测试完成: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("\n✓ 所有测试通过！Anspire Search Agent 集成成功。")
    else:
        print(f"\n✗ 有 {failed} 个测试失败，请检查配置。")
        sys.exit(1)


if __name__ == "__main__":
    main()
