#!/usr/bin/env python3
"""
统一搜索引擎接口

支持多个搜索引擎：
- Anspire Search (优先）
- Brave Search (回退）
"""

import os
from typing import Optional, Dict, Any
from enum import Enum


class SearchEngine(Enum):
    """搜索引擎类型"""
    ANSPIRE = "anspire"
    BRAVE = "brave"


class UnifiedSearchClient:
    """统一搜索客户端"""

    def __init__(
        self,
        anspire_api_key: Optional[str] = None,
        brave_api_key: Optional[str] = None,
        default_engine: SearchEngine = SearchEngine.ANSPIRE
    ):
        """
        初始化客户端

        Args:
            anspire_api_key: Anspire API Key
            brave_api_key: Brave API Key
            default_engine: 默认搜索引擎
        """
        self.default_engine = default_engine

        # Anspire
        self.anspire_api_key = anspire_api_key or os.environ.get("ANSPIRE_API_KEY")
        self.anspire_client = None

        if self.anspire_api_key:
            try:
                from anspire_search import AnspireSearchAgent
                self.anspire_client = AnspireSearchAgent(
                    api_key=self.anspire_api_key,
                    enable_cache=True,
                    enable_intent=True
                )
            except ImportError:
                pass

        # Brave
        self.brave_api_key = brave_api_key or os.environ.get("BRAVE_API_KEY")
        self.brave_client = None

        if self.brave_api_key:
            try:
                from brave_search import BraveSearchClient
                self.brave_client = BraveSearchClient(
                    api_key=self.brave_api_key
                )
            except ImportError:
                pass

    def search(
        self,
        query: str,
        engine: Optional[SearchEngine] = None,
        count: int = 10,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行搜索

        Args:
            query: 搜索查询
            engine: 指定引擎，不指定则使用默认
            count: 返回结果数量
            from_time: 起始时间（Anspire）
            to_time: 结束时间（Anspire）
            **kwargs: 其他参数

        Returns:
            搜索结果字典
        """
        engine = engine or self.default_engine

        # Anspire
        if engine == SearchEngine.ANSPIRE:
            if not self.anspire_client:
                raise RuntimeError("Anspire 客户端未初始化")

            return self.anspire_client.search(
                query=query,
                top_k=count,
                from_time=from_time,
                to_time=to_time,
                **kwargs
            )

        # Brave
        elif engine == SearchEngine.BRAVE:
            if not self.brave_client:
                raise RuntimeError("Brave 客户端未初始化")

            # Brave 时间格式转换
            freshness = None
            if from_time:
                # Anspire 时间格式转 Brave freshnes
                if "p1d" in from_time or "天" in from_time:
                    freshness = "p1d"
                elif "pw" in from_time or "周" in from_time:
                    freshness = "pw"
                elif "pm" in from_time or "月" in from_time:
                    freshness = "pm"
                elif "py" in from_time or "年" in from_time:
                    freshness = "py"

            return self.brave_client.search(
                query=query,
                count=count,
                freshness=freshness,
                **kwargs
            )

        else:
            raise ValueError(f"不支持的搜索引擎: {engine}")

    def search_news(
        self,
        query: str,
        engine: Optional[SearchEngine] = None,
        count: int = 10,
        freshness: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        新闻搜索

        Args:
            query: 搜索查询
            engine: 指定引擎，不指定则使用默认
            count: 返回结果数量
            freshness: 时间新鲜度

        Returns:
            搜索结果字典
        """
        # 优先使用 Anspire
        if engine is None:
            engine = self.default_engine

        # Brave 新闻搜索已修复（使用普通搜索的 news 字段）
        if engine == SearchEngine.BRAVE:
            if self.brave_client:
                return self.brave_client.search_news(
                    query=query,
                    count=count,
                    freshness=freshness or "pw"
                )
            elif self.anspire_client:
                engine = SearchEngine.ANSPIRE

        return self.search(
            query=query,
            engine=engine,
            count=count,
            **kwargs
        )

    def analyze_intent(self, query: str):
        """分析搜索意图"""
        if self.anspire_client:
            return self.anspire_client.analyze_intent(query)
        return None

    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """获取缓存统计"""
        if self.anspire_client:
            return self.anspire_client.get_cache_stats()
        return None


def main():
    """命令行测试"""
    import json

    # 初始化客户端
    client = UnifiedSearchClient()

    print("=== 测试 Anspire 搜索 ===")
    try:
        result = client.search("AI", engine=SearchEngine.ANSPIRE, count=3)
        if "results" in result:
            print(f"✓ Anspire: 找到 {len(result['results'])} 个结果")
        else:
            print(f"✗ Anspire: {result.get('detail', '失败')}")
    except Exception as e:
        print(f"✗ Anspire: {e}")

    print("\n=== 测试 Brave 搜索 ===")
    try:
        result = client.search("AI", engine=SearchEngine.BRAVE, count=3)
        if "web" in result:
            items = result["web"].get("results", [])
            print(f"✓ Brave: 找到 {len(items)} 个结果")
        else:
            print(f"✗ Brave: {result.get('error', '失败')}")
    except Exception as e:
        print(f"✗ Brave: {e}")

    print("\n=== 测试默认引擎（应优先 Anspire） ===")
    try:
        result = client.search("AI", count=3)
        if "results" in result:
            print(f"✓ 默认: 找到 {len(result['results'])} 个结果（使用 Anspire）")
    except Exception as e:
        print(f"✗ 默认: {e}")

    print("\n=== 测试缓存统计 ===")
    stats = client.get_cache_stats()
    if stats:
        print(f"缓存: {stats['total']} 个, {stats['size_mb']} MB")
    else:
        print("缓存未启用")


if __name__ == "__main__":
    main()
