"""M1 Scraper 接口。后续 MediaCrawlerScraper / SaasScraper 都实现这个 Protocol。"""

from __future__ import annotations

from datetime import date
from typing import Protocol

from ..models import RawPost


class Scraper(Protocol):
    """给定 keyword + 目标日期,返回当日发布的帖子(含评论)。

    BLUEPRINT § M1:"给定 keyword + 日期,产出当日帖子 + 评论的 JSONL"
    所有实现均为 async,返回 list[RawPost]。
    watchlist_id 用于落盘时标记数据来源,默认 None。
    """

    async def fetch(
        self,
        keyword: str,
        target_date: date,
        watchlist_id: str | None = None,
    ) -> list[RawPost]:
        ...
