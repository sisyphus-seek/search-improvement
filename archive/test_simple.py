#!/usr/bin/env python3
"""
简单测试脚本 - 验证修改后的搜索工具
"""

import subprocess
import sys

def test_basic_search():
    """测试基本搜索（Anspire）"""
    print("🧪 测试 1: 基本搜索（Anspire）")
    result = subprocess.run(
        ["python3", "prometheus_search.py", "Rust 编程语言", "-c", "3", "-v"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ 失败：{result.stderr}")
    else:
        print("✅ 通过\n")

def test_brave_search():
    """测试 Brave 搜索"""
    print("🧪 测试 2: Brave 搜索")
    result = subprocess.run(
        ["python3", "prometheus_search.py", "Python tutorial", "-e", "brave", "-c", "3"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ 失败：{result.stderr}")
    else:
        print("✅ 通过\n")

def test_auto_mode():
    """测试 auto 模式（应直接使用 Anspire）"""
    print("🧪 测试 3: auto 模式（简化版）")
    result = subprocess.run(
        ["python3", "prometheus_search.py", "AI news", "-e", "auto", "-c", "3", "-v"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ 失败：{result.stderr}")
    else:
        print("✅ 通过\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Prometheus 搜索工具 - 简化版测试")
    print("=" * 60 + "\n")
    
    test_basic_search()
    test_brave_search()
    test_auto_mode()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
