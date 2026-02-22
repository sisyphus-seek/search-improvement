#!/usr/bin/env python3
"""
Brave Search API 客户端

文档: https://api.search.brave.com/app/documentation
API: https://api.search.brave.com/res/v1/web/search

特性：隐私优先、快速、结构化结果
"""

import os
import sys
import json
import requests
from typing import Optional, List, Dict, Any


class BraveSearchClient:
    """Brave Search API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: API Key，如不传则从环境变量 BRAVE_API_KEY 读取
        """
        self.api_key = api_key or os.environ.get("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("API Key 未提供，请设置 BRAVE_API_KEY 环境变量或传入 api_key 参数")

        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }

    def search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
        search_lang: Optional[str] = None,
        result_filter: Optional[str] = None,
        safesearch: str = "moderate",
        freshness: Optional[str] = None,
        country: str = "CN",
        text_decorations: bool = True,
        spellcheck: bool = True
    ) -> Dict[str, Any]:
        """
        执行搜索

        Args:
            query: 搜索查询字符串
            count: 返回结果数量（默认 10，最大 20）
            offset: 分页偏移（默认 0）
            search_lang: 搜索语言（如：zh-CN, en-US）
            result_filter: 结果过滤（web, news, images, videos）
            safesearch: 安全搜索（strict, moderate, off）
            freshness: 时间新鲜度（p1d, pw, pm, py）
            country: 结果国家代码（默认 CN）
            text_decorations: 是否返回文本装饰
            spellcheck: 是否启用拼写检查

        Returns:
            搜索结果字典
        """
        params = {
            "q": query,
            "count": min(count, 20),  # Brave 限制最多 20
            "offset": offset,
            "country": country,
            "text_decorations": str(text_decorations).lower(),
            "spellcheck": str(spellcheck).lower(),
            "safesearch": safesearch
        }

        # 可选参数
        if search_lang:
            params["search_lang"] = search_lang
        if result_filter:
            params["result_filter"] = result_filter
        if freshness:
            params["freshness"] = freshness

        response = requests.get(self.base_url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def search_news(
        self,
        query: str,
        count: int = 10,
        freshness: str = "pw"  # past week
    ) -> Dict[str, Any]:
        """
        新闻搜索

        Args:
            query: 搜索查询字符串
            count: 返回结果数量
            freshness: 时间新鲜度（p1d=past day, pw=past week, pm=past month, py=past year）

        Returns:
            搜索结果字典

        注意：Brave 普通搜索已包含 news 字段，不使用 result_filter=news 避免参数冲突
        """
        result = self.search(
            query=query,
            count=count,
            freshness=freshness,
            search_lang="zh-hans"  # Brave API 使用 zh-hans 而不是 zh-CN
        )

        # 确保 news 字段存在
        if "news" not in result:
            result["news"] = {"results": []}

        return result


def format_result(result: Dict[str, Any]) -> str:
    """
    格式化搜索结果为可读文本

    Args:
        result: API 返回的原始结果

    Returns:
        格式化后的文本
    """
    if "web" not in result and "news" not in result:
        return f"搜索失败: {result.get('error', '未知错误')}"

    # 获取结果列表
    web_results = result.get("web", {}).get("results", [])
    news_results = result.get("news", {}).get("results", [])

    items = web_results if web_results else news_results

    if not items:
        return "未找到相关结果"

    output = []
    output.append(f"找到 {len(items)} 个结果：\n")

    for idx, item in enumerate(items, 1):
        title = item.get("title", "无标题")
        url = item.get("url", "无链接")

        # 尝试获取描述
        description = ""
        if "description" in item:
            description = item.get("description", "")
        elif "snippet" in item:
            description = item.get("snippet", "")

        # 日期（新闻结果）
        date = ""
        if "age" in item:
            date = item.get("age", "")

        output.append(f"## [{idx}] {title}")
        if date:
            output.append(f"**日期**: {date}")
        output.append(f"**来源**: {url}")
        if description:
            preview = description[:200]
            output.append(f"\n{preview}{'...' if len(description) > 200 else ''}\n")

    return "\n".join(output)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Brave Search API - 隐私优先搜索")
    parser.add_argument("query", help="搜索查询")
    parser.add_argument("-c", "--count", type=int, default=10, help="返回结果数量（默认 10，最大 20）")
    parser.add_argument("-n", "--news", action="store_true", help="新闻搜索")
    parser.add_argument("-f", "--freshness", help="时间新鲜度（p1d, pw, pm, py）")
    parser.add_argument("--offset", type=int, default=0, help="分页偏移")
    parser.add_argument("--raw", action="store_true", help="输出原始JSON")

    args = parser.parse_args()

    try:
        client = BraveSearchClient()

        if args.news:
            result = client.search_news(
                query=args.query,
                count=args.count,
                freshness=args.freshness or "pw"
            )
        else:
            result = client.search(
                query=args.query,
                count=args.count,
                freshness=args.freshness
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
