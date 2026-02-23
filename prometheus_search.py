#!/usr/bin/env python3
"""
Prometheus 专用搜索工具

封装 search-improvement 项目能力，提供简洁的命令行接口。
自动从 credentials 目录加载 API Keys。
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
ENGINES_DIR = SRC_DIR / "engines"
UTILS_DIR = SRC_DIR / "utils"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(ENGINES_DIR))
sys.path.insert(0, str(UTILS_DIR))

# 自动加载凭证
CREDENTIALS_DIR = Path(__file__).parent.parent / "credentials"

def load_credentials():
    """从 credentials 目录加载 API Keys"""
    anspire_key = None
    brave_key = None
    
    anspire_file = CREDENTIALS_DIR / "anspire_api_key.txt"
    brave_file = CREDENTIALS_DIR / "brave_api_key.txt"
    
    if anspire_file.exists():
        anspire_key = anspire_file.read_text().strip()
    
    if brave_file.exists():
        brave_key = brave_file.read_text().strip()
    
    # 设置环境变量
    if anspire_key:
        os.environ["ANSPIRE_API_KEY"] = anspire_key
    if brave_key:
        os.environ["BRAVE_API_KEY"] = brave_key
    
    return anspire_key, brave_key


def search(query: str, engine: str = "anspire", count: int = 10, 
           insite: str = None, from_time: str = None, to_time: str = None,
           news: bool = False, raw: bool = False, verbose: bool = False):
    """
    执行搜索
    
    Args:
        query: 搜索查询
        engine: 搜索引擎 (anspire/brave/auto)
        count: 返回结果数量
        insite: 站内搜索
        from_time: 起始时间
        to_time: 结束时间
        news: 是否搜索新闻
        raw: 输出原始 JSON
        verbose: 显示详细过程
    
    Returns:
        搜索结果
    """
    # 加载凭证
    anspire_key, brave_key = load_credentials()
    
    if not anspire_key and not brave_key:
        return {"error": "未找到 API Keys，请检查 credentials 目录"}
    
    # 自动选择引擎 - 简化版（直接默认 Anspire，避免额外的工具调用）
    if engine == "auto":
        # 不再使用意图识别（会消耗额外的工具调用次数）
        # 直接默认使用 Anspire，如有需要可手动指定 brave
        engine = "anspire"
        
        if verbose:
            print(f"[自动选择] 已简化：直接使用 Anspire 引擎（避免额外工具调用）")
    
    # 执行搜索
    try:
        if engine == "anspire":
            from anspire_search import AnspireSearchAgent
            
            agent = AnspireSearchAgent(
                api_key=anspire_key,
                enable_cache=True,
                enable_intent=verbose
            )
            
            if news:
                # Anspire 没有专门的新闻 API，使用普通搜索
                result = agent.search(
                    query=query,
                    top_k=count,
                    from_time=from_time if from_time else "p7d",  # 默认最近 7 天
                    to_time=to_time,
                    verbose=verbose
                )
            else:
                result = agent.search(
                    query=query,
                    top_k=count,
                    insite=insite,
                    from_time=from_time,
                    to_time=to_time,
                    verbose=verbose
                )
        
        elif engine == "brave":
            from brave_search import BraveSearchClient
            
            client = BraveSearchClient(api_key=brave_key)
            
            if news:
                result = client.search_news(
                    query=query,
                    count=count,
                    freshness="pw"  # 默认最近一周
                )
            else:
                result = client.search(
                    query=query,
                    count=count,
                    freshness=from_time
                )
        
        else:
            return {"error": f"不支持的引擎：{engine}"}
        
        return result
    
    except Exception as e:
        return {"error": str(e)}


def format_results(result: dict, engine: str) -> str:
    """格式化搜索结果"""
    if "error" in result:
        return f"❌ 错误：{result['error']}"
    
    output = []
    
    # Anspire 格式
    if "results" in result:
        items = result.get("results", [])
        output.append(f"✅ 找到 {len(items)} 个结果（Anspire）\n")
        
        for idx, item in enumerate(items, 1):
            title = item.get("title", "无标题")
            content = item.get("content", "")[:200]
            url = item.get("url", "")
            date = item.get("date", "")
            
            output.append(f"**{idx}. {title}**")
            if date:
                output.append(f"📅 {date}")
            if url:
                output.append(f"🔗 {url}")
            if content:
                output.append(f"{content}{'...' if len(item.get('content', '')) > 200 else ''}")
            output.append("")
    
    # Brave 格式
    elif "web" in result:
        items = result["web"].get("results", [])
        output.append(f"✅ 找到 {len(items)} 个结果（Brave）\n")
        
        for idx, item in enumerate(items, 1):
            title = item.get("title", "无标题")
            description = item.get("description", item.get("snippet", ""))[:200]
            url = item.get("url", "")
            
            output.append(f"**{idx}. {title}**")
            if url:
                output.append(f"🔗 {url}")
            if description:
                output.append(f"{description}{'...' if len(item.get('description', '') + item.get('snippet', '')) > 200 else ''}")
            output.append("")
    
    # 新闻格式
    elif "news" in result:
        items = result["news"].get("results", [])
        output.append(f"✅ 找到 {len(items)} 条新闻\n")
        
        for idx, item in enumerate(items, 1):
            title = item.get("title", "无标题")
            description = item.get("description", "")[:200]
            url = item.get("url", "")
            age = item.get("age", "")
            
            output.append(f"**{idx}. {title}**")
            if age:
                output.append(f"📅 {age}")
            if url:
                output.append(f"🔗 {url}")
            if description:
                output.append(f"{description}{'...' if len(item.get('description', '')) > 200 else ''}")
            output.append("")
    
    return "\n".join(output)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Prometheus 搜索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "AI 最新进展"                    # 使用 Anspire 搜索
  %(prog)s "Python bug" -e brave           # 使用 Brave 搜索
  %(prog)s "site:github.com openclaw"      # 站内搜索
  %(prog)s "新闻" -n                       # 新闻搜索
  %(prog)s "Rust" -e auto -v               # 简化自动模式（直接使用 Anspire）
        """
    )
    
    parser.add_argument("query", help="搜索查询")
    parser.add_argument("-e", "--engine", default="anspire", 
                        choices=["anspire", "brave", "auto"],
                        help="搜索引擎（默认：anspire；auto=anspire 简化模式）")
    parser.add_argument("-c", "--count", type=int, default=10,
                        help="返回结果数量（默认：10）")
    parser.add_argument("-s", "--insite", help="站内搜索（如：github.com）")
    parser.add_argument("--from-time", help="起始时间")
    parser.add_argument("--to-time", help="结束时间")
    parser.add_argument("-n", "--news", action="store_true", help="新闻搜索")
    parser.add_argument("--raw", action="store_true", help="输出原始 JSON")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细过程")
    
    args = parser.parse_args()
    
    # 执行搜索
    result = search(
        query=args.query,
        engine=args.engine,
        count=args.count,
        insite=args.insite,
        from_time=args.from_time,
        to_time=args.to_time,
        news=args.news,
        verbose=args.verbose
    )
    
    # 输出结果
    if args.raw:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        formatted = format_results(result, args.engine)
        print(formatted)


if __name__ == "__main__":
    main()
