"""daily_run — 每日调度入口,串联 M1 → M2 → M3。

BLUEPRINT § 五 Week 1:
    一条命令 python scripts/daily_run.py --date 2026-05-13 跑通全流程

当前状态: M1 已实现,M2 已实现,M3 预留 pass。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from datetime import date
from pathlib import Path

import yaml

from src.m1_scraper.manual import ManualScraper
from src.m1_scraper.xhs_mcp import XhsMcpScraper
from src.m1_scraper.fallback import FallbackScraper
from src.m0_monitor import KeywordMonitor
from src.models import RawPost, ScoredPost

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def load_watchlist(path: Path = Path("config/watchlist.yaml")) -> list[dict]:
    """读取 watchlist.yaml,返回 enabled=true 的条目。"""
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    entries = data.get("watchlist", [])
    return [e for e in entries if e.get("enabled", False)]


def save_posts_jsonl(posts: list[RawPost], output_path: Path) -> None:
    """将 RawPost 列表写入 JSONL 文件。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for post in posts:
            f.write(post.model_dump_json() + "\n")
    logger.info(f"Saved {len(posts)} posts to {output_path}")


async def run_m1(
    target_date: date,
    watchlist: list[dict],
    mcp_url: str = "http://127.0.0.1:18060/mcp",
) -> dict[str, list[RawPost]]:
    """M1: 对每个 enabled 的 watchlist 条目,逐 keyword 采集帖子。

    返回 {watchlist_id: [RawPost, ...]}
    """
    primary = XhsMcpScraper(mcp_url=mcp_url)
    fallback = ManualScraper()
    scraper = FallbackScraper(primary, fallback)

    all_posts: dict[str, list[RawPost]] = {}

    for entry in watchlist:
        watchlist_id = entry["id"]
        keywords = entry.get("keywords", [])
        posts_for_entry: list[RawPost] = []

        for keyword in keywords:
            logger.info(f"[M1] Fetching watchlist={watchlist_id!r} keyword={keyword!r} date={target_date}")
            try:
                posts = await scraper.fetch(keyword, target_date, watchlist_id=watchlist_id)
                posts_for_entry.extend(posts)
                logger.info(f"[M1] Got {len(posts)} posts for keyword={keyword!r}")
            except Exception as e:
                logger.error(f"[M1] Failed for keyword={keyword!r}: {type(e).__name__}: {e}")

        # 去重 (同一帖子可能被多个 keyword 召回)
        seen_ids: set[str] = set()
        deduped: list[RawPost] = []
        for post in posts_for_entry:
            if post.post_id not in seen_ids:
                seen_ids.add(post.post_id)
                deduped.append(post)

        all_posts[watchlist_id] = deduped

        # 落盘 JSONL
        if deduped:
            output_path = Path("data/raw") / f"{target_date}_{watchlist_id}.jsonl"
            save_posts_jsonl(deduped, output_path)

    return all_posts


def run_m2(
    all_posts: dict[str, list[RawPost]],
    target_date: date,
    monitor: KeywordMonitor | None = None,
    model: str = "mimo-v2.5-pro",
) -> dict[str, list[ScoredPost]]:
    """M2: 情绪打分。使用 LLM 对每条帖子 + 评论区进行多模态情绪分析。

    返回 {watchlist_id: [ScoredPost, ...]}
    写入 data/scored/{date}_{watchlist_id}.jsonl
    """
    from src.m2_sentiment import SentimentEngine

    engine = SentimentEngine(model=model)
    all_scored: dict[str, list[ScoredPost]] = {}
    total_cost = 0.0

    for watchlist_id, posts in all_posts.items():
        scored_posts: list[ScoredPost] = []
        for i, post in enumerate(posts):
            logger.info(
                f"[M2] Scoring {i + 1}/{len(posts)}: post_id={post.post_id} "
                f"keyword={post.keyword!r} ({len(post.comments)} comments)"
            )
            try:
                scored = engine.analyze(post)
                scored_posts.append(scored)
                total_cost += scored.cost_usd

                # Feed is_relevant to KeywordMonitor
                if monitor:
                    monitor.update(post.keyword, scored.is_relevant)

                logger.info(
                    f"[M2] -> sentiment_post={scored.sentiment_post:+d} "
                    f"is_relevant={scored.is_relevant} "
                    f"fomo={scored.fomo} cost=${scored.cost_usd:.4f}"
                )
            except Exception as e:
                logger.error(f"[M2] Failed scoring post {post.post_id}: {e}")

        all_scored[watchlist_id] = scored_posts

        # Write scored JSONL
        if scored_posts:
            scored_dir = Path("data/scored")
            scored_dir.mkdir(parents=True, exist_ok=True)
            output_path = scored_dir / f"{target_date}_{watchlist_id}.jsonl"
            with output_path.open("w", encoding="utf-8") as f:
                for sp in scored_posts:
                    f.write(sp.model_dump_json() + "\n")
            logger.info(f"[M2] Saved {len(scored_posts)} scored posts to {output_path}")

    logger.info(f"[M2] Total LLM cost: ${total_cost:.4f}")
    if total_cost > 1.0:
        logger.warning(f"[M2] Daily cost ${total_cost:.2f} exceeds $1 budget!")

    return all_scored


def run_m3(all_scored: dict[str, list[ScoredPost]], target_date: date, db_path: str = "data/metrics.db") -> None:
    """M3: 日度聚合写入 SQLite。"""
    from src.m3_aggregate import DailyAggregator

    aggregator = DailyAggregator(db_path=db_path)

    for watchlist_id, scored_posts in all_scored.items():
        logger.info(f"[M3] Aggregating watchlist={watchlist_id!r} ({len(scored_posts)} scored posts)")
        metric = aggregator.aggregate(scored_posts, target_date=target_date)
        logger.info(
            f"[M3] -> n_posts={metric.n_posts} "
            f"sentiment_combined={metric.sentiment_combined:+.4f} "
            f"top_quotes={json.loads(metric.top_quotes_json)}"
        )


async def main_async(target_date: date, mcp_url: str, model: str = "mimo-v2.5-pro") -> None:
    watchlist = load_watchlist()
    if not watchlist:
        logger.warning("No enabled watchlist entries. Check config/watchlist.yaml")
        return

    logger.info(f"=== Daily Run: {target_date} ===")
    logger.info(f"Enabled watchlists: {[e['id'] for e in watchlist]}")

    # M1
    all_posts = await run_m1(target_date, watchlist, mcp_url=mcp_url)

    # M2 + KeywordMonitor
    monitor = KeywordMonitor(threshold=0.5)
    all_scored = run_m2(all_posts, target_date, monitor=monitor, model=model)

    # M3
    run_m3(all_scored, target_date)

    # KeywordMonitor summary
    alerts = monitor.check_and_alert()
    if alerts:
        logger.warning(f"[Monitor] Noisy keywords: {alerts}")
    logger.info(f"\n{monitor.summary()}")

    # Summary
    total = sum(len(posts) for posts in all_posts.values())
    logger.info(f"=== Done: {total} total posts across {len(all_posts)} watchlists ===")


def main() -> None:
    parser = argparse.ArgumentParser(description="rednote_monitor 每日调度")
    parser.add_argument(
        "--date",
        default=None,
        help="目标日期 YYYY-MM-DD (默认: 今天)",
    )
    parser.add_argument(
        "--mcp-url",
        default="http://127.0.0.1:18060/mcp",
        help="xiaohongshu-mcp 服务地址",
    )
    parser.add_argument(
        "--model",
        default="mimo-v2.5-pro",
        help="LLM model for sentiment scoring (default: mimo-v2.5-pro)",
    )
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else date.today()
    asyncio.run(main_async(target_date, args.mcp_url, model=args.model))


if __name__ == "__main__":
    main()
