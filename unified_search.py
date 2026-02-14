#!/usr/bin/env python3
"""
统一的搜索接口
支持多个搜索源，自动选择最佳源
"""

import json
import urllib.parse
from typing import List, Dict, Optional, Any

# 假设我们有 web_fetch 函数（需要从 OpenClaw 工具集成）
# 为了测试，这里先定义一个模拟版本
def web_fetch(url: str, extractMode: str = "text", maxChars: int = 5000) -> str:
    """
    模拟 web_fetch 函数
    实际使用时应该调用 OpenClaw 的 web_fetch 工具
    """
    import subprocess
    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True,
        text=True,
        timeout=10
    )
    return result.stdout


class SearchResult:
    """搜索结果"""
    def __init__(self, title: str, url: str, snippet: str = "", source: str = ""):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source

    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source
        }


class SearchSource:
    """搜索源基类"""
    def __init__(self, name: str):
        self.name = name
        self.success_rate = 1.0  # 成功率
        self.failure_count = 0
        self.success_count = 0

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """执行搜索，由子类实现"""
        raise NotImplementedError

    def record_success(self):
        """记录成功"""
        self.success_count += 1
        self.success_rate = self.success_count / (self.success_count + self.failure_count)

    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.success_rate = self.success_count / (self.success_count + self.failure_count)


class GitHubSearchSource(SearchSource):
    """GitHub 搜索源"""
    def __init__(self):
        super().__init__("GitHub")

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.github.com/search/repositories?q={encoded_query}&per_page={limit}"
            response = web_fetch(url, extractMode="text")

            data = json.loads(response)
            results = []

            for item in data.get("items", []):
                result = SearchResult(
                    title=item.get("name", ""),
                    url=item.get("html_url", ""),
                    snippet=item.get("description", ""),
                    source=self.name
                )
                results.append(result)

            self.record_success()
            return results[:limit]

        except Exception as e:
            self.record_failure()
            print(f"[{self.name}] Error: {e}")
            return []


class HackerNewsSearchSource(SearchSource):
    """Hacker News 搜索源"""
    def __init__(self):
        super().__init__("Hacker News")

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://hn.algolia.com/api/v1/search?query={encoded_query}&hitsPerPage={limit}"
            response = web_fetch(url, extractMode="text")

            data = json.loads(response)
            results = []

            for item in data.get("hits", []):
                result = SearchResult(
                    title=item.get("title", item.get("story_title", "")),
                    url=item.get("url", item.get("story_url", "")),
                    snippet=item.get("comment_text", "")[:200] if item.get("comment_text") else "",
                    source=self.name
                )
                results.append(result)

            self.record_success()
            return results[:limit]

        except Exception as e:
            self.record_failure()
            print(f"[{self.name}] Error: {e}")
            return []


class DuckDuckGoSearchSource(SearchSource):
    """DuckDuckGo 搜索源"""
    def __init__(self):
        super().__init__("DuckDuckGo")

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://duckduckgo.com/html/?q={encoded_query}"
            response = web_fetch(url, extractMode="text")

            # 简单解析（实际需要更复杂的解析）
            results = []
            lines = response.split('\n')

            for line in lines:
                # 查找包含标题和链接的行
                if 'duckduckgo.com/l/?uddg=' in line:
                    # 解析链接
                    import re
                    match = re.search(r'//duckduckgo\.com/l/\?uddg=([^&\s]+)', line)
                    if match:
                        encoded_url = match.group(1)
                        real_url = urllib.parse.unquote(encoded_url)

                        # 提取标题（简化版）
                        title = line.strip()
                        if title:
                            result = SearchResult(
                                title=title[:100],
                                url=real_url,
                                snippet="",
                                source=self.name
                            )
                            results.append(result)

                        if len(results) >= limit:
                            break

            self.record_success()
            return results[:limit]

        except Exception as e:
            self.record_failure()
            print(f"[{self.name}] Error: {e}")
            return []


class UnifiedSearchEngine:
    """统一搜索引擎"""
    def __init__(self):
        self.sources: List[SearchSource] = [
            GitHubSearchSource(),
            HackerNewsSearchSource(),
            DuckDuckGoSearchSource(),
        ]

    def search(
        self,
        query: str,
        preferred_source: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        执行搜索

        Args:
            query: 搜索查询
            preferred_source: 首选搜索源（GitHub, Hacker News, DuckDuckGo）
            limit: 返回结果数量

        Returns:
            搜索结果列表
        """
        # 如果指定了首选源，只使用该源
        if preferred_source:
            for source in self.sources:
                if source.name == preferred_source:
                    results = source.search(query, limit)
                    if results:
                        return results

        # 否则，按成功率排序尝试所有源
        sorted_sources = sorted(
            self.sources,
            key=lambda s: s.success_rate,
            reverse=True
        )

        all_results = []

        for source in sorted_sources:
            results = source.search(query, limit)
            all_results.extend(results)
            if len(all_results) >= limit:
                break

        # 去重
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result.url and result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)

        return unique_results[:limit]

    def get_status(self) -> Dict[str, Any]:
        """获取所有搜索源的状态"""
        return {
            source.name: {
                "success_rate": source.success_rate,
                "success_count": source.success_count,
                "failure_count": source.failure_count,
            }
            for source in self.sources
        }


# 测试代码
if __name__ == "__main__":
    engine = UnifiedSearchEngine()

    print("=== 测试搜索 ===\n")

    # 测试 GitHub 搜索
    print("[GitHub] 搜索 'nowledge mem':")
    results = engine.search("nowledge mem", preferred_source="GitHub", limit=5)
    for r in results:
        print(f"  - {r.title}: {r.url}")

    # 测试 Hacker News 搜索
    print("\n[Hacker News] 搜索 'LLM':")
    results = engine.search("LLM", preferred_source="Hacker News", limit=5)
    for r in results:
        print(f"  - {r.title}: {r.url}")

    # 测试 DuckDuckGo 搜索
    print("\n[DuckDuckGo] 搜索 'python tutorial':")
    results = engine.search("python tutorial", preferred_source="DuckDuckGo", limit=5)
    for r in results:
        print(f"  - {r.title}: {r.url}")

    # 测试自动选择
    print("\n[自动选择] 搜索 'AI agent':")
    results = engine.search("AI agent", limit=10)
    for r in results:
        print(f"  [{r.source}] {r.title}: {r.url}")

    # 显示状态
    print("\n=== 搜索源状态 ===")
    status = engine.get_status()
    for source_name, metrics in status.items():
        print(f"{source_name}:")
        print(f"  成功率: {metrics['success_rate']:.2%}")
        print(f"  成功: {metrics['success_count']}")
        print(f"  失败: {metrics['failure_count']}")
