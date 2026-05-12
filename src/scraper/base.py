"""M1 Scraper 接口。后续 MediaCrawlerScraper / SaasScraper 都实现这个 Protocol。"""

from __future__ import annotations

from datetime import date
from typing import Protocol

from ..models import RawPost


class Scraper(Protocol):
    """给定 keyword + 目标日期,返回当日发布的帖子(含评论)。

    BLUEPRINT § M1:"给定 keyword + 日期,产出当日帖子 + 评论的 JSONL"
    实现方可以同步可以异步,只要返回 list[RawPost] 即可。
    """

    def fetch(self, keyword: str, target_date: date) -> list[RawPost]:
        ...
