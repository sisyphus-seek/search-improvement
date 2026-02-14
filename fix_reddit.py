#!/usr/bin/env python3
"""
修复 Reddit API - 添加 User-Agent 和其他头部
"""
import urllib.request
import urllib.parse
import json
import ssl

def fetch_with_headers(url):
    """使用浏览器头部获取内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    req = urllib.request.Request(url, headers=headers)

    # 忽略 SSL 验证（仅用于测试）
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=10, context=context) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"


def test_reddit_search():
    """测试 Reddit 搜索"""
    query = "machine learning"
    url = f"https://www.reddit.com/search.json?q={urllib.parse.quote(query)}&limit=5"

    print(f"测试 URL: {url}\n")

    response = fetch_with_headers(url)

    print("响应内容（前 500 字符）：")
    print(response[:500])

    if response.startswith("Error"):
        print("\n❌ 请求失败")
        return False

    try:
        data = json.loads(response)
        print("\n✅ JSON 解析成功")
        print(f"数据结构: {list(data.keys())}")

        if 'data' in data:
            children = data['data'].get('children', [])
            print(f"找到 {len(children)} 个结果")

            for i, item in enumerate(children[:3], 1):
                post = item.get('data', {})
                print(f"\n{i}. {post.get('title', 'N/A')}")
                print(f"   Score: {post.get('score', 0)}")
                print(f"   URL: {post.get('url', 'N/A')}")

        return True
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON 解析失败: {e}")
        print("响应类型: HTML 而非 JSON（可能需要认证）")
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("Reddit API 修复测试")
    print("=" * 80)
    print()

    success = test_reddit_search()

    print("\n" + "=" * 80)
    if success:
        print("✅ Reddit API 修复成功")
    else:
        print("❌ Reddit API 仍需进一步调试")
    print("=" * 80)
