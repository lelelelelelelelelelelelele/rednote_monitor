"""FallbackScraper — 带降级逻辑的 Scraper。

BLUEPRINT § 风险 1: 小红书反爬地狱级，M1 无论选哪个方案都会断更。
对策: ManualScraper 永远保留，真 Scraper 挂掉时降级到人工 30 分钟/天。

实现方式: 优先用 XhsMcpScraper，失败时自动降级到 ManualScraper。
"""

from __future__ import annotations

import logging
from datetime import date

from .base import Scraper
from .manual import ManualScraper
from .xhs_mcp import XhsMcpScraper
from ..models import RawPost

logger = logging.getLogger(__name__)


class FallbackScraper:
    """带降级逻辑的 Scraper: 优先用 XhsMcpScraper，失败时降级到 ManualScraper。

    使用示例::

        primary = XhsMcpScraper()
        fallback = ManualScraper()
        scraper = FallbackScraper(primary, fallback)

        posts = await scraper.fetch("甲骨文", date(2026, 5, 13))
    """

    def __init__(
        self,
        primary: XhsMcpScraper,
        fallback: ManualScraper,
        logger: logging.Logger | None = None,
    ):
        self.primary = primary
        self.fallback = fallback
        self.logger = logger or logging.getLogger(__name__)

    async def fetch(
        self,
        keyword: str,
        target_date: date,
        watchlist_id: str | None = None,
    ) -> list[RawPost]:
        """先尝试 primary (XhsMcpScraper)，失败时降级到 fallback (ManualScraper)。

        降级条件:
        1. primary.fetch() 抛出异常 (网络错误、MCP 服务未启动等)
        2. primary.fetch() 返回空列表 (可能是因为反爬导致采集中断)
        """
        try:
            posts = await self.primary.fetch(keyword, target_date, watchlist_id=watchlist_id)
            if posts:
                return posts
            self.logger.warning(
                f"[FallbackScraper] Primary scraper returned empty for "
                f"keyword={keyword!r}, date={target_date}. Falling back to ManualScraper."
            )
        except Exception as e:
            self.logger.error(
                f"[FallbackScraper] Primary scraper failed for "
                f"keyword={keyword!r}, date={target_date}: {type(e).__name__}: {e}. "
                f"Falling back to ManualScraper."
            )

        # 降级到 ManualScraper
        return await self.fallback.fetch(keyword, target_date)
