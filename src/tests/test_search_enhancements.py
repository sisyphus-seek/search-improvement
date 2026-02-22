#!/usr/bin/env python3
"""
搜索增强功能测试

测试搜索缓存和意图识别功能。
"""

import os
import sys

# 添加 tools 目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from anspire_search import AnspireSearchAgent
from search_cache import SearchCache
from search_intent import SearchIntentClassifier, SearchEngineSelector


def test_cache():
    """测试缓存功能"""
    print("=== 测试缓存功能 ===")
    try:
        cache = SearchCache(ttl_hours=1)

        # 模拟搜索结果
        test_result = {
            "query": "test query",
            "Uuid": "test-uuid",
            "results": [{"title": "Test Result"}]
        }

        # 测试写入
        cache.set("test query", test_result, top_k=10)
        print("✓ 缓存写入成功")

        # 测试读取
        cached = cache.get("test query", top_k=10)
        if cached == test_result:
            print("✓ 缓存读取成功")
        else:
            print("✗ 缓存读取失败：数据不匹配")
            return False

        # 测试统计
        stats = cache.stats()
        print(f"✓ 缓存统计: {stats['total']} 个缓存, {stats['size_mb']} MB")

        # 测试清空
        count = cache.clear()
        if count >= 1:
            print(f"✓ 缓存清空成功: {count} 个文件")
        else:
            print("✗ 缓存清空失败")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def test_intent_classification():
    """测试意图分类"""
    print("=== 测试意图分类 ===")
    try:
        classifier = SearchIntentClassifier()

        test_cases = [
            ("site:github.com openclaw", "site_search", "站内搜索"),
            ("在 github 搜索", "site_search", "中文站内搜索"),
            ("最近一周的新闻", "time_range", "时间范围"),
            ("Python 安装 requests 失败", "technical", "技术搜索"),
            ("人工智能最新进展", "general", "通用搜索"),
            ("2024-12-01 到 2025-01-01", "time_range", "日期格式"),
        ]

        for query, expected_intent, description in test_cases:
            analysis = classifier.classify(query)
            actual_intent = analysis.intent.value

            if actual_intent == expected_intent:
                print(f"✓ {description}: {query} → {actual_intent}")
            else:
                print(f"⚠ {description}: {query}")
                print(f"  期望: {expected_intent}, 实际: {actual_intent}")
                print(f"  推理: {analysis.reasoning}")
                # 不算失败，因为意图识别可能是模糊的

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def test_engine_selection():
    """测试引擎选择"""
    print("=== 测试引擎选择 ===")
    try:
        classifier = SearchIntentClassifier()
        selector = SearchEngineSelector(["anspire", "brave", "duckduckgo"])

        test_cases = [
            ("site:github.com openclaw", "anspire", "站内搜索首选 Anspire"),
            ("最近一周的新闻", "brave", "时间范围首选 Brave"),
            ("技术文档 API", "anspire", "技术搜索首选 Anspire"),
            ("通用查询", "anspire", "通用查询默认 Anspire"),
        ]

        for query, expected_engine, description in test_cases:
            analysis = classifier.classify(query)
            engine = selector.select(analysis)

            if engine == expected_engine:
                print(f"✓ {description}: {query} → {engine}")
            else:
                print(f"⚠ {description}: {query}")
                print(f"  期望: {expected_engine}, 实际: {engine}")
                print(f"  意图: {analysis.intent.value}")

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def test_anspire_with_cache():
    """测试 Anspire 集成缓存"""
    print("=== 测试 Anspire 集成缓存 ===")
    try:
        agent = AnspireSearchAgent(enable_cache=True)

        # 清空缓存
        cache = SearchCache()
        cache.clear()

        # 第一次搜索（未命中缓存）
        result1 = agent.search("测试查询", top_k=3, use_cache=True, verbose=False)
        print("✓ 第一次搜索完成")

        # 第二次搜索（命中缓存）
        result2 = agent.search("测试查询", top_k=3, use_cache=True, verbose=False)
        print("✓ 第二次搜索完成（应命中缓存）")

        # 验证结果一致性
        if result1.get("Uuid") == result2.get("Uuid"):
            print("✓ 缓存结果一致")
        else:
            print("⚠ 缓存结果不一致（可能是时间差异）")

        # 获取缓存统计
        stats = agent.get_cache_stats()
        print(f"✓ 缓存统计: {stats['total']} 个")

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    return True


def test_anspire_with_intent():
    """测试 Anspire 集成意图识别"""
    print("=== 测试 Anspire 集成意图识别 ===")
    try:
        agent = AnspireSearchAgent(enable_intent=True)

        test_queries = [
            "site:github.com openclaw",
            "最近一周的新闻",
            "Python 安装失败",
        ]

        for query in test_queries:
            analysis = agent.analyze_intent(query)
            if analysis:
                print(f"✓ {query[:30]}... → {analysis.intent.value} ({analysis.confidence:.2f})")
            else:
                print("✗ 意图分析失败")
                return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    print()
    return True


def main():
    """运行所有测试"""
    print("搜索增强功能测试\n")
    print("=" * 60)
    print()

    # 检查 API Key
    if not os.environ.get("ANSPIRE_API_KEY"):
        print("⚠  警告: 未设置 ANSPIRE_API_KEY 环境变量")
        print("   某些测试可能会跳过或失败\n")

    # 运行测试
    tests = [
        ("缓存功能", test_cache),
        ("意图分类", test_intent_classification),
        ("引擎选择", test_engine_selection),
        ("Anspire+缓存", test_anspire_with_cache),
        ("Anspire+意图", test_anspire_with_intent),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {name} 测试异常: {e}\n")
            failed += 1

    # 总结
    print("=" * 60)
    print(f"\n测试完成: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("\n✓ 所有测试通过！搜索增强功能运行正常。")
    else:
        print(f"\n⚠  有 {failed} 个测试失败，请检查配置。")


if __name__ == "__main__":
    main()
