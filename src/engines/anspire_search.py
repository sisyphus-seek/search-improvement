#!/usr/bin/env python3
"""
Anspire Search Agent - 智能搜索工具

文档: https://open.anspire.cn/document/docs/searchApi/
API: https://plugin.anspire.cn/api/ntsearch/search

✅ 测试通过: 基本搜索、站内搜索、多站搜索
⚠️  注意: 时间范围参数可能不稳定，建议谨慎使用
"""

import os
import sys
import json
import requests
from typing import Optional, List, Dict, Any

# 导入缓存和意图识别模块
try:
    from search_cache import SearchCache, get_default_cache
    from search_intent import SearchIntentClassifier, SearchEngineSelector, SearchIntent
except ImportError:
    # 如果模块不存在，使用空实现
    SearchCache = None
    SearchIntentClassifier = None
    SearchEngineSelector = None


class AnspireSearchAgent:
    """Anspire Search Agent 客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        enable_cache: bool = True,
        enable_intent: bool = True
    ):
        """
        初始化客户端

        Args:
            api_key: API Key，如不传则从环境变量 ANSPIRE_API_KEY 读取
            enable_cache: 是否启用缓存
            enable_intent: 是否启用意图识别
        """
        self.api_key = api_key or os.environ.get("ANSPIRE_API_KEY")
        if not self.api_key:
            raise ValueError("API Key 未提供，请设置 ANSPIRE_API_KEY 环境变量或传入 api_key 参数")

        self.base_url = "https://plugin.anspire.cn/api/ntsearch/search"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "*/*"
        }

        # 初始化缓存
        self.enable_cache = enable_cache and SearchCache is not None
        self.cache = get_default_cache() if self.enable_cache else None

        # 初始化意图识别
        self.enable_intent = enable_intent and SearchIntentClassifier is not None
        self.intent_classifier = SearchIntentClassifier() if self.enable_intent else None
        self.engine_selector = SearchEngineSelector(["anspire", "brave", "duckduckgo"]) if self.enable_intent else None

    def search(
        self,
        query: str,
        top_k: int = 10,
        insite: Optional[str] = None,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        use_cache: bool = True,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        执行搜索

        Args:
            query: 搜索查询字符串（不超过64个字符）
            top_k: 返回结果数量（10/20/30/40/50），默认10
            insite: 站内搜索限制（最多20个站点，用逗号分隔）
            from_time: 搜索时间范围起始时间
                       支持格式：
                       - ISO 8601: "2025-01-01T00:00:00" (推荐)
                       - 仅日期: "2025-01-01"
                       - Unix 时间戳: "1704067200"
            to_time: 搜索时间范围结束时间
                     支持格式：同 from_time
            use_cache: 是否使用缓存
            verbose: 是否输出详细过程

        Returns:
            搜索结果字典
        """
        # 意图识别
        if self.enable_intent and verbose:
            analysis = self.intent_classifier.classify(query)
            print(f"[意图] {analysis.intent.value} (置信度: {analysis.confidence:.2f})")
            print(f"[推理] {analysis.reasoning}")

            # 检查是否适合用当前引擎
            recommended_engine = self.engine_selector.select(analysis)
            if recommended_engine != "anspire":
                print(f"[提示] 推荐使用 {recommended_engine} 引擎")

        # 检查缓存
        if use_cache and self.cache:
            cached = self.cache.get(query, top_k, insite, from_time, to_time)
            if cached:
                if verbose:
                    print("[缓存] 命中缓存")
                return cached
            elif verbose:
                print("[缓存] 未命中")

        # 执行搜索
        params = {
            "query": query[:64],  # 限制64字符
            "top_k": str(top_k)
        }

        # 站内搜索（可用）
        if insite:
            params["Insite"] = insite

        # 时间范围（需要使用正确格式）
        if from_time:
            params["FromTime"] = from_time
        if to_time:
            params["ToTime"] = to_time

        response = requests.get(self.base_url, params=params, headers=self.headers)
        response.raise_for_status()
        result = response.json()

        # 保存到缓存
        if use_cache and self.cache:
            self.cache.set(query, result, top_k, insite, from_time, to_time)
            if verbose:
                print("[缓存] 已保存")

        return result

    def search_multi_site(
        self,
        query: str,
        sites: List[str],
        top_k: int = 10,
        use_cache: bool = True,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        多站内搜索

        Args:
            query: 搜索查询字符串
            sites: 网站列表（最多20个）
            top_k: 返回结果数量
            use_cache: 是否使用缓存
            verbose: 是否输出详细过程

        Returns:
            搜索结果字典
        """
        insite = ",".join(sites[:20])  # 最多20个站点
        return self.search(query, top_k=top_k, insite=insite, use_cache=use_cache, verbose=verbose)

    def analyze_intent(self, query: str):
        """分析搜索意图"""
        if not self.intent_classifier:
            return None
        return self.intent_classifier.classify(query)

    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """获取缓存统计"""
        if not self.cache:
            return None
        return self.cache.stats()


def format_result(result: Dict[str, Any]) -> str:
    """
    格式化搜索结果为可读文本

    Args:
        result: API 返回的原始结果

    Returns:
        格式化后的文本
    """
    if "results" not in result:
        return f"搜索失败: {result.get('detail', '未知错误')}"

    items = result.get("results", [])

    if not items:
        return "未找到相关结果"

    output = []
    output.append(f"找到 {len(items)} 个结果：\n")

    for idx, item in enumerate(items, 1):
        title = item.get("title", "无标题")
        content = item.get("content", "无内容")
        url = item.get("url", "无链接")
        date = item.get("date", "未知")

        output.append(f"## [{idx}] {title}")
        output.append(f"**日期**: {date}")
        output.append(f"**来源**: {url}")
        output.append(f"\n{content[:200]}{'...' if len(content) > 200 else ''}\n")

    return "\n".join(output)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Anspire Search Agent - 智能搜索")
    parser.add_argument("query", nargs="?", help="搜索查询（不超过64字符），某些操作不需要")
    parser.add_argument("-k", "--top-k", type=int, default=10, help="返回结果数量（10/20/30/40/50，默认10）")
    parser.add_argument("-s", "--insite", help="站内搜索限制（多个站点用逗号分隔）")
    parser.add_argument("--from-time", help="搜索起始时间（如：2025-01-01 00:00:00）【可能不稳定】")
    parser.add_argument("--to-time", help="搜索结束时间（如：2025-02-01 00:00:00）【可能不稳定】")
    parser.add_argument("--raw", action="store_true", help="输出原始JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细过程（意图识别、缓存状态）")
    parser.add_argument("--no-cache", action="store_true", help="不使用缓存")
    parser.add_argument("--intent", action="store_true", help="仅分析搜索意图，不执行搜索")
    parser.add_argument("--cache-stats", action="store_true", help="显示缓存统计")

    args = parser.parse_args()

    try:
        agent = AnspireSearchAgent(enable_cache=not args.no_cache)

        # 缓存统计
        if args.cache_stats:
            stats = agent.get_cache_stats()
            if stats:
                print("缓存统计：")
                print(f"  总数: {stats['total']}")
                print(f"  有效: {stats['valid']}")
                print(f"  过期: {stats['expired']}")
                print(f"  大小: {stats['size_mb']} MB")
            else:
                print("缓存未启用")
            return

        # 意图分析
        if args.intent:
            analysis = agent.analyze_intent(args.query)
            if analysis:
                print(f"意图: {analysis.intent.value}")
                print(f"置信度: {analysis.confidence:.2f}")
                print(f"推理: {analysis.reasoning}")
                if analysis.sites:
                    print(f"站点: {', '.join(analysis.sites)}")
                if analysis.keywords:
                    print(f"关键词: {', '.join(analysis.keywords)}")
            else:
                print("意图识别未启用")
            return

        # 执行搜索
        result = agent.search(
            query=args.query,
            top_k=args.top_k,
            insite=args.insite,
            from_time=args.from_time,
            to_time=args.to_time,
            use_cache=not args.no_cache,
            verbose=args.verbose
        )

        if args.raw:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(format_result(result))

    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"网络错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
