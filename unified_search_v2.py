#!/usr/bin/env python3
"""
统一的搜索接口 v2
支持多个搜索源，自动选择最佳源
新增：Reddit 和 Stack Overflow 支持
"""

import json
import urllib.parse
import re
from typing import List, Dict, Optional, Any

# 模拟 web_fetch（实际应使用 OpenClaw 工具）
def web_fetch(url: str, extractMode: str = "text", maxChars: int = 5000, headers: Dict = None) -> str:
    """
    模拟 web_fetch 函数
    实际使用时应该调用 OpenClaw 的 web_fetch 工具
    """
    import subprocess

    cmd = ["curl", "-s", "-L", url]

    if headers:
        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10
    )
    return result.stdout


class SearchResult:
    """搜索结果"""
    def __init__(self, title: str, url: str, snippet: str = "", source: str = "", metadata: Dict = None):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "metadata": self.metadata
        }


class SearchSource:
    """搜索源基类"""
    def __init__(self, name: str):
        self.name = name
        self.success_rate = 1.0
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
                    source=self.name,
                    metadata={
                        "stars": item.get("stargazers_count", 0),
                        "language": item.get("language", ""),
                        "updated_at": item.get("updated_at", "")
                    }
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
                    source=self.name,
                    metadata={
                        "points": item.get("points", 0),
                        "author": item.get("author", ""),
                        "created_at": item.get("created_at", "")
                    }
                )
                results.append(result)

            self.record_success()
            return results[:limit]

        except Exception as e:
            self.record_failure()
            print(f"[{self.name}] Error: {e}")
            return []


class RedditSearchSource(SearchSource):
    """Reddit 搜索源"""
    def __init__(self):
        super().__init__("Reddit")

        # Reddit 需要特殊的 User-Agent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
        }

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.reddit.com/search.json?q={encoded_query}&limit={limit}"
            response = web_fetch(url, extractMode="text", headers=self.headers)

            data = json.loads(response)
            results = []

            for item in data.get("data", {}).get("children", []):
                post_data = item.get("data", {})
                title = post_data.get("title", "")
                url = post_data.get("url", "")
                snippet = post_data.get("selftext", "")[:200] if post_data.get("selftext") else ""
                subreddit = post_data.get("subreddit", "")

                if title and url:
                    result = SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        source=f"{self.name}/r/{subreddit}",
                        metadata={
                            "score": post_data.get("score", 0),
                            "subreddit": subreddit,
                            "author": post_data.get("author", ""),
                            "created_utc": post_data.get("created_utc", "")
                        }
                    )
                    results.append(result)

            self.record_success()
            return results[:limit]

        except Exception as e:
            self.record_failure()
            print(f"[{self.name}] Error: {e}")
            return []


class StackOverflowSearchSource(SearchSource):
    """Stack Overflow 搜索源"""
    def __init__(self):
        super().__init__("Stack Overflow")

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=activity&accepted=True&answers=1&title={encoded_query}&site=stackoverflow&pagesize={limit}"
            response = web_fetch(url, extractMode="text")

            data = json.loads(response)
            results = []

            for item in data.get("items", []):
                title = item.get("title", "")
                question_id = item.get("question_id", "")
                url = f"https://stackoverflow.com/questions/{question_id}"

                result = SearchResult(
                    title=title,
                    url=url,
                    snippet=item.get("excerpt", "")[:200] if item.get("excerpt") else "",
                    source=self.name,
                    metadata={
                        "score": item.get("score", 0),
                        "answer_count": item.get("answer_count", 0),
                        "tags": item.get("tags", [])
                    }
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

            results = []

            # 改进的解析逻辑
            lines = response.split('\n')
            current_title = ""

            for line in lines:
                # 提取标题
                if '<a rel="nofollow" class="result__a"' in line:
                    title_match = re.search(r'>([^<]+)</a>', line)
                    if title_match:
                        current_title = title_match.group(1).strip()

                # 提取链接
                if 'duckduckgo.com/l/?uddg=' in line and current_title:
                    link_match = re.search(r'//duckduckgo\.com/l/\?uddg=([^&\s"]+)', line)
                    if link_match:
                        encoded_url = link_match.group(1)
                        real_url = urllib.parse.unquote(encoded_url)

                        result = SearchResult(
                            title=current_title,
                            url=real_url,
                            snippet="",
                            source=self.name
                        )
                        results.append(result)
                        current_title = ""

                        if len(results) >= limit:
                            break

            self.record_success()
            return results[:limit]

        except Exception as e:
            self.record_failure()
            print(f"[{self.name}] Error: {e}")
            return []


class UnifiedSearchEngine:
    """统一搜索引擎 v2"""
    def __init__(self):
        self.sources: List[SearchSource] = [
            GitHubSearchSource(),
            HackerNewsSearchSource(),
            RedditSearchSource(),
            StackOverflowSearchSource(),
            DuckDuckGoSearchSource(),
        ]

        # 查询类型到搜索源的映射
        self.query_type_mapping = {
            "code": ["GitHub", "Stack Overflow"],
            "news": ["Hacker News", "Reddit"],
            "general": ["DuckDuckGo", "Reddit"],
        }

    def detect_query_type(self, query: str) -> str:
        """
        检测查询类型

        Returns: "code", "news", or "general"
        """
        query_lower = query.lower()

        # 代码相关关键词
        code_keywords = [
            "api", "function", "library", "package", "module",
            "class", "method", "bug", "error", "exception",
            "github", "stackoverflow", "pip", "npm", "cargo",
            "python", "javascript", "golang", "rust", "java"
        ]

        # 新闻相关关键词
        news_keywords = [
            "release", "launch", "announced", "breaking",
            "news", "startup", "funding", "acquired"
        ]

        code_score = sum(1 for kw in code_keywords if kw in query_lower)
        news_score = sum(1 for kw in news_keywords if kw in query_lower)

        if code_score > news_score:
            return "code"
        elif news_score > code_score:
            return "news"
        else:
            return "general"

    def search(
        self,
        query: str,
        preferred_source: Optional[str] = None,
        limit: int = 10,
        query_type: Optional[str] = None
    ) -> List[SearchResult]:
        """
        执行搜索

        Args:
            query: 搜索查询
            preferred_source: 首选搜索源
            limit: 返回结果数量
            query_type: 查询类型（自动检测或指定）

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
            return []

        # 检测查询类型
        if query_type is None:
            query_type = self.detect_query_type(query)

        # 根据查询类型选择搜索源
        preferred_sources = self.query_type_mapping.get(query_type, [])

        # 构建待尝试的搜索源列表
        # 优先使用类型匹配的源，然后按成功率排序
        type_matches = [s for s in self.sources if s.name in preferred_sources]
        others = [s for s in self.sources if s.name not in preferred_sources]

        sorted_type_matches = sorted(type_matches, key=lambda s: s.success_rate, reverse=True)
        sorted_others = sorted(others, key=lambda s: s.success_rate, reverse=True)

        sources_to_try = sorted_type_matches + sorted_others

        all_results = []

        for source in sources_to_try:
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
                "success_rate": f"{source.success_rate:.2%}",
                "success_count": source.success_count,
                "failure_count": source.failure_count,
            }
            for source in self.sources
        }


# 测试代码
if __name__ == "__main__":
    engine = UnifiedSearchEngine()

    print("=" * 60)
    print("统一搜索引擎 v2 - 测试")
    print("=" * 60)

    # 测试 1: 代码查询（应该优先 GitHub/Stack Overflow）
    print("\n[测试 1] 代码查询 'nowledge mem':")
    print("预期: GitHub → Stack Overflow")
    query_type = engine.detect_query_type("nowledge mem")
    print(f"检测类型: {query_type}")
    results = engine.search("nowledge mem", limit=5)
    for r in results:
        print(f"  [{r.source}] {r.title}")
        if r.metadata:
            print(f"    {r.url}")

    # 测试 2: 新闻查询（应该优先 Hacker News/Reddit）
    print("\n[测试 2] 新闻查询 'AI agent release':")
    print("预期: Hacker News → Reddit")
    query_type = engine.detect_query_type("AI agent release")
    print(f"检测类型: {query_type}")
    results = engine.search("AI agent release", limit=5)
    for r in results:
        print(f"  [{r.source}] {r.title}")

    # 测试 3: 通用查询（应该优先 DuckDuckGo/Reddit）
    print("\n[测试 3] 通用查询 'best python tutorial':")
    print("预期: DuckDuckGo → Reddit")
    query_type = engine.detect_query_type("best python tutorial")
    print(f"检测类型: {query_type}")
    results = engine.search("best python tutorial", limit=5)
    for r in results:
        print(f"  [{r.source}] {r.title}")

    # 测试 4: Stack Overflow 查询
    print("\n[测试 4] Stack Overflow 'python exception':")
    results = engine.search("python exception", preferred_source="Stack Overflow", limit=3)
    for r in results:
        print(f"  [{r.source}] {r.title}")
        print(f"    {r.url}")

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
