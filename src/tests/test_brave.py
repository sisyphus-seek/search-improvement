#!/usr/bin/env python3
"""
Brave Search API 测试脚本

运行前请设置环境变量：
export BRAVE_API_KEY="your-api-key-here"
"""

import os
import sys
from brave_search import BraveSearchClient


def test_basic_search():
    """测试基本搜索"""
    print("=== 测试基本搜索 ===")
    try:
        client = BraveSearchClient()
        result = client.search("AI", count=3)

        if "web" in result:
            items = result["web"].get("results", [])
            print(f"✓ 基本搜索成功")
            print(f"  找到 {len(items)} 个结果")
            if items:
                print(f"  第一个结果: {items[0]['title'][:50]}...")
        else:
            print(f"✗ 搜索失败: {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def test_news_search():
    """测试新闻搜索"""
    print("=== 测试新闻搜索 ===")
    try:
        client = BraveSearchClient()
        result = client.search_news("AI", count=3)

        # 检查 web 和 news 字段
        web_items = result.get("web", {}).get("results", [])
        news_items = result.get("news", {}).get("results", [])

        print(f"✓ 新闻搜索成功")
        print(f"  Web 结果: {len(web_items)} 个")
        print(f"  News 结果: {len(news_items)} 个")

        if news_items:
            print(f"  第一个新闻: {news_items[0]['title'][:50]}...")

        if web_items or news_items:
            return True
        else:
            print(f"⚠ 未找到结果")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def test_freshness():
    """测试时间新鲜度"""
    print("=== 测试时间新鲜度 ===")
    try:
        client = BraveSearchClient()

        # 测试过去一天
        result = client.search("新闻", count=3, freshness="p1d")

        if "web" in result:
            items = result["web"].get("results", [])
            print(f"✓ 时间新鲜度搜索成功")
            print(f"  找到 {len(items)} 个结果")
        else:
            print(f"✗ 搜索失败: {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def test_pagination():
    """测试分页"""
    print("=== 测试分页 ===")
    try:
        client = BraveSearchClient()

        # 第一页
        result1 = client.search("AI", count=3, offset=0)
        items1 = result1.get("web", {}).get("results", [])

        # 第二页
        result2 = client.search("AI", count=3, offset=3)
        items2 = result2.get("web", {}).get("results", [])

        if items1 and items2:
            # 验证不重复
            urls1 = {item["url"] for item in items1}
            urls2 = {item["url"] for item in items2}

            if not urls1.intersection(urls2):
                print(f"✓ 分页成功（无重复）")
                print(f"  第一页: {len(items1)} 个结果")
                print(f"  第二页: {len(items2)} 个结果")
            else:
                print(f"⚠ 分页结果有重复")
        else:
            print(f"✗ 分页失败")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def main():
    """运行所有测试"""
    print("Brave Search API 测试\n")
    print("=" * 50)
    print()

    # 检查 API Key
    if not os.environ.get("BRAVE_API_KEY"):
        print("错误: 未设置 BRAVE_API_KEY 环境变量")
        print("\n请先获取 API Key:")
        print("  1. 访问 https://search.brave.com/search/api")
        print("  2. 注册并获取免费 API Key")
        print("  3. 运行: export BRAVE_API_KEY='your-key-here'")
        sys.exit(1)

    # 运行测试
    tests = [
        test_basic_search,
        test_news_search,
        test_freshness,
        test_pagination
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
        print("\n✓ 所有测试通过！Brave Search API 集成成功。")
    else:
        print(f"\n✗ 有 {failed} 个测试失败，请检查配置。")
        sys.exit(1)


if __name__ == "__main__":
    main()
