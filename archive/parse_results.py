#!/usr/bin/env python3
import re
from html.parser import HTMLParser

# 从 web_fetch 的结果中提取链接
html_content = """
Nowledge Mem - Think, Remember, Connect
 //duckduckgo.com/l/?uddg=https%3A%2F%2Fmem.nowledge.co%2F&rut=0448bd42a33607914c53793313282ddd84d300dfc4a087a742fdbe50aae1524c
 mem.nowledge.co
 Memory and context manager just works. Your Knowledge, your Control, Graph Augmented.

Nowledge Mem - GitHub
 //duckduckgo.com/l/?uddg=https%3A%2F%2Fgithub.com%2Fnowledge%2Dco%2Fnowledge%2Dmem&rut=f0c23d90e724030f291826f1966d8e6b6a09ad90e1c0d280ad6149249e0071b3
 github.com/nowledge-co/nowledge-mem
 Nowledge Mem is a local-first, graph-augmented personal context manager that preserves conversations and insights from your AI interactions. Stop opening 5 AI apps to find that one conversation. Type → found. Mem can persist entire conversation threads across all your AI tools while also distilling key insights into searchable memories. Everything connected through an intelligent knowledge ...

Introducing Nowledge Mem - Nowledge Labs | Nowledge Labs
 //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.nowledge%2Dlabs.ai%2Fblog%2Fnowledge%2Dmem&rut=2177c23c3a800a3c56d93bc805aa07cc40282e1261bfe76ca75d2a3cdcadca83
 www.nowledge-labs.ai/blog/nowledge-mem
 The graph augmented, smart and local-first personal context manager just works.

Nowledge Mem: Local-First AI Conversation & Context Manager
 //duckduckgo.com/l/?uddg=https%3A%2F%2Fmcpmarket.com%2Fserver%2Fnowledge%2Dmem&rut=037124422489a98d0764a685f8366583a5308c88310707895f916b019b5c983b
 mcpmarket.com/server/nowledge-mem
 About Nowledge Mem is a privacy-first, graph-native, and AI-integrated personal context manager designed to centralize and preserve all your AI interactions. It solves problem of scattered conversations across multiple AI apps by allowing users to capture entire conversation threads and distill key insights. Everything is connected through an intelligent knowledge graph, enabling ...

Nowledge Mem
 //duckduckgo.com/l/?uddg=https%3A%2F%2Fmcp.so%2Fserver%2Fnowledge%2Dmem%2FNowledge%2520Labs%2C%2520LLC&rut=cada79b9891a399b2e59fd1554293c972abccb2433f567978bda23b191430b32
 mcp.so/server/nowledge-mem/Nowledge Labs, LLC
 Nowledge Mem is a graph-augmented, smart, and local-first personal context manager that helps users manage and augment their personal context across different tools and agents, all while ensuring data is stored locally with on-device AI models.

nowledge-mem · PyPI
 //duckduckgo.com/l/?uddg=https%3A%2F%2Fpypi.org%2Fproject%2Fnowledge%2Dmem%2F&rut=f96425d1ed0fe1d484bfda97cb313f01d58b60d175ea0eb971860f98593c902e
 pypi.org/project/nowledge-mem/
 2025-10-02T00:00:00.00000000
 A Python MCP server for Nowledge Mem

Overview | Nowledge Mem
 //duckduckgo.com/l/?uddg=https%3A%2F%2Fmem.nowledge.co%2Fdocs&rut=b88c33506f9ec05a82be53b0d27167883c65fdc2b12bd93ced00e2387c20e752
 mem.nowledge.co/docs
 The Nowledge Graph is a hyper-connected knowledge graph that intelligently links memories, threads, messages, and extracted entities through meaningful relationships.

Nowledge Mem: AI knowledge & context manager, local-first.
 //duckduckgo.com/l/?uddg=https%3A%2F%2Faikii.org%2Fproducts%2Fnowledge%2Dmem&rut=e2cd357ea5b5a5b513a78cae4895a13c9bcc272278755669060911d115264fd6
 aikii.org/products/nowledge-mem
 Nowledge Mem is a local-first AI knowledge & context manager using graph-enhanced tech to build personal knowledge systems. Features: smart search, Agent integration via MCP, visual graph
"""

# 解析 uddg 参数提取真实 URL
import urllib.parse

def extract_real_url(redirect_url):
    """从 DuckDuckGo 重定向 URL 中提取真实 URL"""
    match = re.search(r'uddg=([^&]+)', redirect_url)
    if match:
        encoded = match.group(1)
        return urllib.parse.unquote(encoded)
    return None

# 提取结果
print("搜索 'nowledge mem wiki' 结果：\n")

results = [
    ("Nowledge Mem - Think, Remember, Connect", "mem.nowledge.co"),
    ("Nowledge Mem - GitHub", "github.com/nowledge-co/nowledge-mem"),
    ("Introducing Nowledge Mem", "www.nowledge-labs.ai/blog/nowledge-mem"),
    ("Nowledge Mem: Local-First AI Conversation", "mcpmarket.com/server/nowledge-mem"),
    ("Nowledge Mem", "mcp.so/server/nowledge-mem"),
    ("nowledge-mem · PyPI", "pypi.org/project/nowledge-mem"),
    ("Overview | Nowledge Mem", "mem.nowledge.co/docs"),
    ("Nowledge Mem: AI knowledge manager", "aikii.org/products/nowledge-mem"),
]

for i, (title, url) in enumerate(results, 1):
    print(f"{i}. {title}")
    print(f"   {url}")
    print()

print("\n**Nowledge Mem 是什么？**")
print("=" * 50)
print("Nowledge Mem 是一个本地优先（local-first）、图增强的个人上下文管理器。")
print("")
print("主要特点：")
print("- 保存和管理 AI 对话记录和洞察")
print("- 支持多个 AI 工具的对话线程持久化")
print("- 将关键洞察提取为可搜索的记忆")
print("- 通过智能知识图连接所有内容")
print("- 本地优先，数据隐私保护")
print("- 支持 MCP (Model Context Protocol) 集成")
print("")
print("**主要链接：**")
print("- 官网: https://mem.nowledge.co")
print("- GitHub: https://github.com/nowledge-co/nowledge-mem")
print("- PyPI: https://pypi.org/project/nowledge-mem")
