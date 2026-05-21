"""手动测试 M1 Scraper 功能。

使用方式:
    # 确保 xiaohongshu-mcp 已启动 (http://127.0.0.1:18060/mcp)
    uv run python tests/m1_scraper/test_manual.py

    # 指定 keyword 和日期
    uv run python tests/m1_scraper/test_manual.py --keyword 甲骨文 --date 2026-05-13

    # 使用 ManualScraper 测试
    uv run python tests/m1_scraper/test_manual.py --scraper manual
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import date

from src.m1_scraper.manual import ManualScraper
from src.m1_scraper.xhs_mcp import XhsMcpScraper
from src.m1_scraper.fallback import FallbackScraper
from src.m0_monitor import KeywordMonitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def run_xhs_mcp_scraper(keyword: str, target_date: date) -> None:
    """测试 XhsMcpScraper。"""
    logger.info(f"=== Testing XhsMcpScraper ===")
    logger.info(f"Keyword: {keyword}, Date: {target_date}")

    scraper = XhsMcpScraper()
    posts = await scraper.fetch(keyword, target_date)

    logger.info(f"Found {len(posts)} posts")
    for i, post in enumerate(posts[:5], 1):
        logger.info(f"  [{i}] {post.title[:60]}...")
        logger.info(f"      Likes: {post.n_likes}, Comments: {len(post.comments)}")
        if post.comments:
            logger.info(f"      Top comment: {post.comments[0].text[:50]}...")

    return posts


async def run_manual_scraper(keyword: str, target_date: date) -> None:
    """测试 ManualScraper。"""
    logger.info(f"=== Testing ManualScraper ===")
    logger.info(f"Keyword: {keyword}, Date: {target_date}")

    scraper = ManualScraper()
    posts = await scraper.fetch(keyword, target_date)

    logger.info(f"Found {len(posts)} posts")
    for i, post in enumerate(posts[:5], 1):
        logger.info(f"  [{i}] {post.title[:60]}...")
        logger.info(f"      Likes: {post.n_likes}, Comments: {len(post.comments)}")

    return posts


async def run_fallback_scraper(keyword: str, target_date: date) -> None:
    """测试 FallbackScraper。"""
    logger.info(f"=== Testing FallbackScraper ===")
    logger.info(f"Keyword: {keyword}, Date: {target_date}")

    primary = XhsMcpScraper()
    fallback = ManualScraper()
    scraper = FallbackScraper(primary, fallback)

    posts = await scraper.fetch(keyword, target_date)

    logger.info(f"Found {len(posts)} posts")
    for i, post in enumerate(posts[:5], 1):
        logger.info(f"  [{i}] {post.title[:60]}...")

    return posts


def test_keyword_monitor() -> None:
    """测试 KeywordMonitor。"""
    logger.info(f"=== Testing KeywordMonitor ===")

    monitor = KeywordMonitor(threshold=0.5)

    # 模拟一些数据
    test_data = [
        ("甲骨文", True),
        ("甲骨文", True),
        ("甲骨文", False),
        ("机器人", True),
        ("机器人", False),
        ("机器人", False),
    ]

    for keyword, is_relevant in test_data:
        monitor.update(keyword, is_relevant)

    logger.info(f"Monitor summary:\n{monitor.summary()}")

    alerts = monitor.check_and_alert()
    if alerts:
        logger.warning(f"Alerts: {alerts}")
    else:
        logger.info("No alerts")


def main():
    parser = argparse.ArgumentParser(description="手动测试 M1 Scraper")
    parser.add_argument(
        "--keyword",
        default="甲骨文",
        help="测试关键词 (默认: 甲骨文)",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="目标日期 YYYY-MM-DD (默认: 2026-05-13)",
    )
    parser.add_argument(
        "--scraper",
        choices=["xhs_mcp", "manual", "fallback", "all"],
        default="all",
        help="测试哪个 scraper (默认: all)",
    )
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else date(2026, 5, 13)

    if args.scraper in ("xhs_mcp", "all"):
        asyncio.run(run_xhs_mcp_scraper(args.keyword, target_date))

    if args.scraper in ("manual", "all"):
        asyncio.run(run_manual_scraper(args.keyword, target_date))

    if args.scraper in ("fallback", "all"):
        asyncio.run(run_fallback_scraper(args.keyword, target_date))

    if args.scraper == "all":
        test_keyword_monitor()


if __name__ == "__main__":
    main()
