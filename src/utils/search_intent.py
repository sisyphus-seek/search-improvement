#!/usr/bin/env python3
"""
搜索意图识别与智能引擎选择

根据查询内容和特征，识别搜索意图并选择最合适的搜索引擎。
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SearchIntent(Enum):
    """搜索意图类型"""
    GENERAL = "general"  # 通用搜索
    SITE_SEARCH = "site_search"  # 站内搜索
    MULTI_SITE = "multi_site"  # 多站搜索
    TIME_RANGE = "time_range"  # 时间范围搜索
    TECHNICAL = "technical"  # 技术搜索（代码、API 等）
    NEWS = "news"  # 新闻搜索
    REFERENCE = "reference"  # 参考资料/学术搜索


@dataclass
class IntentAnalysis:
    """意图分析结果"""
    intent: SearchIntent
    confidence: float  # 置信度 0-1
    sites: List[str]  # 识别到的站点
    time_range: Optional[Tuple[str, str]]  # 时间范围 (from, to)
    keywords: List[str]  # 关键词
    reasoning: str  # 推理说明


class SearchIntentClassifier:
    """搜索意图分类器"""

    # 站内搜索模式
    SITE_PATTERNS = [
        r'site:([^\s]+)',  # site:example.com
        r'在([^\s]+)(搜索|查找|找)',  # 在 github 搜索
    ]

    # 时间范围关键词
    TIME_RANGE_KEYWORDS = {
        'recent': ['最近', '近期', 'latest', 'recent'],
        'today': ['今天', 'today'],
        'week': ['本周', 'this week', '这一周'],
        'month': ['本月', 'this month', '这个月'],
        'year': ['今年', 'this year'],
    }

    # 技术搜索关键词
    TECH_KEYWORDS = [
        'api', 'sdk', 'library', '框架', 'framework',
        '代码', 'code', 'github', 'stack overflow',
        'python', 'javascript', 'typescript', 'java',
        'bug', 'error', 'exception', 'issue',
        '安装', 'install', '配置', 'config',
        '文档', 'doc', 'tutorial', '教程',
    ]

    # 新闻搜索关键词
    NEWS_KEYWORDS = [
        '新闻', 'news', '报道', '最新', '发布',
        '消息', '公告', '公告', '动态',
    ]

    # 常见站点
    KNOWN_SITES = [
        'github.com', 'stackoverflow.com', 'pypi.org', 'npmjs.com',
        'docs.python.org', 'developer.mozilla.org', 'open.anspire.cn',
        'docs.openclaw.ai', 'clawhub.com',
    ]

    def classify(self, query: str) -> IntentAnalysis:
        """
        分类搜索意图

        Args:
            query: 搜索查询

        Returns:
            意图分析结果
        """
        query_lower = query.lower()

        # 1. 检查站内搜索
        site_result = self._check_site_search(query, query_lower)
        if site_result:
            return site_result

        # 2. 检查多站搜索
        multi_site_result = self._check_multi_site(query, query_lower)
        if multi_site_result:
            return multi_site_result

        # 3. 检查时间范围
        time_result = self._check_time_range(query, query_lower)
        if time_result:
            return time_result

        # 4. 检查技术搜索
        tech_score = self._score_technical(query, query_lower)

        # 5. 检查新闻搜索
        news_score = self._score_news(query, query_lower)

        # 6. 综合判断
        return self._decide_intent(query, query_lower, tech_score, news_score)

    def _check_site_search(
        self,
        query: str,
        query_lower: str
    ) -> Optional[IntentAnalysis]:
        """检查站内搜索"""
        # 检查 site: 语法
        match = re.search(r'site:([^\s]+)', query_lower)
        if match:
            site = match.group(1)
            return IntentAnalysis(
                intent=SearchIntent.SITE_SEARCH,
                confidence=0.95,
                sites=[site],
                time_range=None,
                keywords=[],
                reasoning=f"检测到 site: 语法，站内搜索: {site}"
            )

        # 检查中文站内搜索语法
        for pattern in self.SITE_PATTERNS[1:]:
            match = re.search(pattern, query)
            if match:
                site = match.group(1)
                return IntentAnalysis(
                    intent=SearchIntent.SITE_SEARCH,
                    confidence=0.90,
                    sites=[site],
                    time_range=None,
                    keywords=[],
                    reasoning=f"检测到中文站内搜索语法: {site}"
                )

        return None

    def _check_multi_site(
        self,
        query: str,
        query_lower: str
    ) -> Optional[IntentAnalysis]:
        """检查多站搜索"""
        # 检查是否包含多个已知站点
        found_sites = []
        for site in self.KNOWN_SITES:
            if site in query_lower:
                found_sites.append(site)

        if len(found_sites) >= 2:
            return IntentAnalysis(
                intent=SearchIntent.MULTI_SITE,
                confidence=0.85,
                sites=found_sites,
                time_range=None,
                keywords=found_sites,
                reasoning=f"检测到多个已知站点: {', '.join(found_sites)}"
            )

        return None

    def _check_time_range(
        self,
        query: str,
        query_lower: str
    ) -> Optional[IntentAnalysis]:
        """检查时间范围"""
        # 检查时间关键词
        time_keywords = []
        for category, keywords in self.TIME_RANGE_KEYWORDS.items():
            for kw in keywords:
                if kw in query_lower:
                    time_keywords.append(kw)

        if time_keywords:
            return IntentAnalysis(
                intent=SearchIntent.TIME_RANGE,
                confidence=0.80,
                sites=[],
                time_range=None,
                keywords=time_keywords,
                reasoning=f"检测到时间关键词: {', '.join(time_keywords)}"
            )

        # 检查日期格式
        date_pattern = r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}'
        dates = re.findall(date_pattern, query)
        if len(dates) >= 1:
            return IntentAnalysis(
                intent=SearchIntent.TIME_RANGE,
                confidence=0.75,
                sites=[],
                time_range=None,
                keywords=dates,
                reasoning=f"检测到日期: {', '.join(dates)}"
            )

        return None

    def _score_technical(self, query: str, query_lower: str) -> float:
        """技术搜索评分"""
        score = 0.0
        matched_keywords = []

        for kw in self.TECH_KEYWORDS:
            if kw in query_lower:
                score += 0.1
                matched_keywords.append(kw)

        # 检查代码相关模式
        if re.search(r'\b(function|class|import|from|def)\b', query_lower):
            score += 0.2
            matched_keywords.append('代码片段')

        # 检查错误信息
        if re.search(r'\b(error|exception|failed|错误|失败)\b', query_lower):
            score += 0.15
            matched_keywords.append('错误信息')

        return min(score, 1.0), matched_keywords

    def _score_news(self, query: str, query_lower: str) -> float:
        """新闻搜索评分"""
        score = 0.0
        matched_keywords = []

        for kw in self.NEWS_KEYWORDS:
            if kw in query_lower:
                score += 0.15
                matched_keywords.append(kw)

        return min(score, 1.0), matched_keywords

    def _decide_intent(
        self,
        query: str,
        query_lower: str,
        tech_score: float,
        news_score: float
    ) -> IntentAnalysis:
        """综合判断意图"""
        tech_score, tech_keywords = tech_score
        news_score, news_keywords = news_score

        # 高置信度判断
        if tech_score >= 0.4:
            return IntentAnalysis(
                intent=SearchIntent.TECHNICAL,
                confidence=tech_score,
                sites=[],
                time_range=None,
                keywords=tech_keywords,
                reasoning=f"技术搜索，关键词: {', '.join(tech_keywords)}"
            )

        if news_score >= 0.3:
            return IntentAnalysis(
                intent=SearchIntent.NEWS,
                confidence=news_score,
                sites=[],
                time_range=None,
                keywords=news_keywords,
                reasoning=f"新闻搜索，关键词: {', '.join(news_keywords)}"
            )

        # 默认通用搜索
        return IntentAnalysis(
            intent=SearchIntent.GENERAL,
            confidence=0.5,
            sites=[],
            time_range=None,
            keywords=[],
            reasoning="通用搜索"
        )


class SearchEngineSelector:
    """搜索引擎选择器"""

    def __init__(self, available_engines: List[str]):
        """
        初始化引擎选择器

        Args:
            available_engines: 可用的搜索引擎列表
        """
        self.available_engines = available_engines

    def select(self, analysis: IntentAnalysis) -> str:
        """
        根据意图选择搜索引擎

        Args:
            analysis: 意图分析结果

        Returns:
            推荐的搜索引擎名称
        """
        # 站内搜索：优先 Anspire
        if analysis.intent == SearchIntent.SITE_SEARCH:
            if "anspire" in self.available_engines:
                return "anspire"
            elif "brave" in self.available_engines:
                return "brave"

        # 多站搜索：仅 Anspire 支持
        if analysis.intent == SearchIntent.MULTI_SITE:
            if "anspire" in self.available_engines:
                return "anspire"

        # 时间范围：Anspire 不稳定，优先其他
        if analysis.intent == SearchIntent.TIME_RANGE:
            if "brave" in self.available_engines:
                return "brave"
            elif "anspire" in self.available_engines:
                return "anspire"  # 作为备选

        # 技术搜索：优先 Anspire（AI 增强）
        if analysis.intent == SearchIntent.TECHNICAL:
            if "anspire" in self.available_engines:
                return "anspire"

        # 新闻搜索：可用任意引擎
        if analysis.intent == SearchIntent.NEWS:
            if "anspire" in self.available_engines:
                return "anspire"

        # 默认：按优先级
        for engine in self.available_engines:
            return engine

        return "anspire"  # 默认值

    def get_fallback_chain(self, analysis: IntentAnalysis) -> List[str]:
        """
        获取回退引擎链

        Args:
            analysis: 意图分析结果

        Returns:
            引擎列表（按优先级）
        """
        selected = self.select(analysis)
        fallback_order = [e for e in self.available_engines if e != selected]

        return [selected] + fallback_order


# 示例使用
if __name__ == "__main__":
    classifier = SearchIntentClassifier()
    selector = SearchEngineSelector(["anspire", "brave", "duckduckgo"])

    # 测试查询
    test_queries = [
        "site:github.com openclaw",
        "github stackoverflow API",
        "最近一周的新闻",
        "Python 安装 requests 失败",
        "人工智能最新进展",
        "在 open.anspire.cn 和 docs.openclaw.ai 搜索",
    ]

    print("搜索意图识别测试\n")
    print("=" * 60)

    for query in test_queries:
        analysis = classifier.classify(query)
        engine = selector.select(analysis)
        fallback = selector.get_fallback_chain(analysis)

        print(f"\n查询: {query}")
        print(f"意图: {analysis.intent.value}")
        print(f"置信度: {analysis.confidence:.2f}")
        print(f"推荐引擎: {engine}")
        print(f"回退链: {' -> '.join(fallback)}")
        print(f"推理: {analysis.reasoning}")

        if analysis.sites:
            print(f"站点: {', '.join(analysis.sites)}")
