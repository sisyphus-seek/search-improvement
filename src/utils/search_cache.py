#!/usr/bin/env python3
"""
搜索结果缓存

提供搜索结果的缓存功能，避免重复请求相同查询。
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class SearchCache:
    """搜索结果缓存"""

    def __init__(
        self,
        cache_dir: str = "/workspace/.workspace/cache/search",
        ttl_hours: int = 24
    ):
        """
        初始化缓存

        Args:
            cache_dir: 缓存目录
            ttl_hours: 缓存有效期（小时）
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(
        self,
        query: str,
        top_k: int,
        insite: Optional[str] = None,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None
    ) -> str:
        """
        生成缓存键

        Args:
            query: 搜索查询
            top_k: 返回数量
            insite: 站内搜索
            from_time: 起始时间
            to_time: 结束时间

        Returns:
            缓存键（MD5 哈希）
        """
        # 构建唯一标识
        params = {
            "query": query,
            "top_k": top_k,
            "insite": insite,
            "from_time": from_time,
            "to_time": to_time
        }

        # JSON 序列化后哈希
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()

    def get(
        self,
        query: str,
        top_k: int = 10,
        insite: Optional[str] = None,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取缓存结果

        Args:
            query: 搜索查询
            top_k: 返回数量
            insite: 站内搜索
            from_time: 起始时间
            to_time: 结束时间

        Returns:
            缓存结果，如果不存在或已过期则返回 None
        """
        cache_key = self._get_cache_key(query, top_k, insite, from_time, to_time)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # 检查是否过期
            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            if datetime.now() - cached_at > timedelta(hours=self.ttl_hours):
                cache_file.unlink()  # 删除过期缓存
                return None

            return cache_data["result"]
        except Exception:
            # 缓存文件损坏，删除
            cache_file.unlink(missing_ok=True)
            return None

    def set(
        self,
        query: str,
        result: Dict[str, Any],
        top_k: int = 10,
        insite: Optional[str] = None,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None
    ) -> None:
        """
        保存缓存结果

        Args:
            query: 搜索查询
            result: 搜索结果
            top_k: 返回数量
            insite: 站内搜索
            from_time: 起始时间
            to_time: 结束时间
        """
        cache_key = self._get_cache_key(query, top_k, insite, from_time, to_time)
        cache_file = self.cache_dir / f"{cache_key}.json"

        cache_data = {
            "query": query,
            "cached_at": datetime.now().isoformat(),
            "ttl_hours": self.ttl_hours,
            "result": result
        }

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

    def clear(self) -> int:
        """
        清空所有缓存

        Returns:
            删除的缓存文件数量
        """
        count = 0
        for file in self.cache_dir.glob("*.json"):
            file.unlink()
            count += 1
        return count

    def clear_expired(self) -> int:
        """
        清空过期缓存

        Returns:
            删除的缓存文件数量
        """
        count = 0
        now = datetime.now()

        for file in self.cache_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                cached_at = datetime.fromisoformat(cache_data["cached_at"])
                if now - cached_at > timedelta(hours=self.ttl_hours):
                    file.unlink()
                    count += 1
            except Exception:
                file.unlink(missing_ok=True)
                count += 1

        return count

    def stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        total = 0
        expired = 0
        size_bytes = 0

        now = datetime.now()

        for file in self.cache_dir.glob("*.json"):
            total += 1
            size_bytes += file.stat().st_size

            try:
                with open(file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                cached_at = datetime.fromisoformat(cache_data["cached_at"])
                if now - cached_at > timedelta(hours=self.ttl_hours):
                    expired += 1
            except Exception:
                pass

        return {
            "total": total,
            "expired": expired,
            "valid": total - expired,
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / 1024 / 1024, 2),
            "cache_dir": str(self.cache_dir)
        }


# 默认缓存实例
_default_cache: Optional[SearchCache] = None


def get_default_cache() -> SearchCache:
    """获取默认缓存实例"""
    global _default_cache
    if _default_cache is None:
        _default_cache = SearchCache()
    return _default_cache


def main():
    """命令行测试"""
    import argparse

    parser = argparse.ArgumentParser(description="搜索结果缓存管理")
    parser.add_argument("action", choices=["stats", "clear", "clear-expired"],
                        help="操作：stats(统计), clear(清空), clear-expired(清空过期)")

    args = parser.parse_args()

    cache = SearchCache()

    if args.action == "stats":
        stats = cache.stats()
        print("缓存统计：")
        print(f"  总数: {stats['total']}")
        print(f"  有效: {stats['valid']}")
        print(f"  过期: {stats['expired']}")
        print(f"  大小: {stats['size_mb']} MB")
        print(f"  目录: {stats['cache_dir']}")

    elif args.action == "clear":
        count = cache.clear()
        print(f"已清空 {count} 个缓存文件")

    elif args.action == "clear-expired":
        count = cache.clear_expired()
        print(f"已清空 {count} 个过期缓存文件")


if __name__ == "__main__":
    main()
