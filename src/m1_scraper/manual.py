"""ManualScraper — M1 的兜底实现,从 data/raw/manual/*_detail.json 解析 RawPost。

BLUEPRINT § M1:
    > ManualScraper:读 data/raw/manual/{date}_{keyword}.txt
    > 第一周必做,解锁所有下游模块

实际数据形态(我们已落盘的)用的是 *.json 而非 *.txt,因为 xiaohongshu-mcp 返回结构化 JSON,
没必要先转纯文本再回来。函数签名仍按 BLUEPRINT 走 (keyword, date) -> list[RawPost]。

文件命名约定(由调用方在落盘时遵守):
    data/raw/manual/test_{YYYYMMDD}_{watchlist_id}_feed_{post_id_prefix}_detail.json

每个 detail 文件顶层包含 _meta.keyword / _meta.watchlist_id,parse 时取这两个字段做匹配。
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

from ..models import RawPost, parse_xhs_feed_detail

logger = logging.getLogger(__name__)


class ManualScraper:
    """读 manual_dir 下的 detail.json,转 RawPost。"""

    def __init__(self, manual_dir: Path | str = Path("data/raw/manual")):
        self.manual_dir = Path(manual_dir)

    # ----- BLUEPRINT 接口 ----- #

    async def fetch(
        self,
        keyword: str,
        target_date: date,
        watchlist_id: str | None = None,
    ) -> list[RawPost]:
        """按 keyword + publish_date 精确过滤。

        注意:publish_date 是帖子的发布日(UTC+8),不是抓取日。manual 数据是历史快照,
        想拿"今天发布"的帖子通常拿不到 —— 这是 M1 真 scraper 替代的核心动机。
        watchlist_id 参数保持接口一致,ManualScraper 不使用它(从 _meta 读取)。
        """
        return [
            post
            for post in self._iter_all_posts()
            if post.keyword == keyword and post.publish_date == target_date
        ]

    # ----- 离线转换工具 ----- #

    def dump_all(
        self,
        output_dir: Path | str = Path("data/raw"),
        run_date: date | None = None,
    ) -> dict[str, Path]:
        """扫描 manual_dir 所有 detail.json,按 watchlist_id 分桶,各写一个 jsonl。

        输出文件名:`{run_date}_{watchlist_id}.jsonl`(run_date 默认今天)。
        返回 {watchlist_id: path} 方便下游知道写到了哪里。
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        run_date = run_date or date.today()

        buckets: dict[str, list[RawPost]] = {}
        for post in self._iter_all_posts():
            key = post.watchlist_id or "_unknown"
            buckets.setdefault(key, []).append(post)

        written: dict[str, Path] = {}
        for watchlist_id, posts in buckets.items():
            out_path = output_dir / f"{run_date}_{watchlist_id}.jsonl"
            with out_path.open("w", encoding="utf-8") as f:
                for post in posts:
                    f.write(post.model_dump_json() + "\n")
            written[watchlist_id] = out_path

        return written

    # ----- 内部 ----- #

    def _iter_all_posts(self) -> Iterable[RawPost]:
        for path in sorted(self.manual_dir.glob("*_detail.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                logger.warning(f"[ManualScraper] skip malformed json: {path.name} ({e})")
                continue

            meta = payload.get("_meta", {})
            keyword = meta.get("keyword", "")
            watchlist_id = meta.get("watchlist_id")
            xsec_token = meta.get("xsec_token")
            fetched_at = self._parse_fetched_at(meta.get("fetched_at"))

            try:
                yield parse_xhs_feed_detail(
                    payload,
                    keyword=keyword,
                    watchlist_id=watchlist_id,
                    xsec_token=xsec_token,
                    fetched_at=fetched_at,
                )
            except Exception as e:
                logger.warning(f"[ManualScraper] skip unparseable: {path.name} ({type(e).__name__}: {e})")

    @staticmethod
    def _parse_fetched_at(s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            return datetime.fromisoformat(s)
        except ValueError:
            return None
