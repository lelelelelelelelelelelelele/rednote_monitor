"""XhsMcpScraper — 通过 xiaohongshu-mcp 采集小红书帖子。

将手动调用 MCP 工具的流程固化为可重复运行的代码：
  1. search_feeds → 获取帖子列表
  2. 按 publish_time 过滤 target_date
  3. get_feed_detail → 获取详情
  4. parse_xhs_feed_detail → 解析为 RawPost
  5. 落盘到 data/raw/manual/ 目录

依赖本地运行的 xiaohongshu-mcp 服务 (默认 http://127.0.0.1:18060/mcp)。
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path

import httpx

from ..models import RawPost, _post_id_to_unix_ms, _ms_to_cn_date, parse_xhs_feed_detail

logger = logging.getLogger(__name__)


class XhsMcpScraper:
    """通过 xiaohongshu-mcp 采集小红书帖子。"""

    def __init__(
        self,
        mcp_url: str = "http://127.0.0.1:18060/mcp",
        manual_dir: Path | str = Path("data/raw/manual"),
        timeout: float = 30.0,
    ):
        self.mcp_url = mcp_url
        self.manual_dir = Path(manual_dir)
        self.timeout = timeout

    async def fetch(
        self,
        keyword: str,
        target_date: date,
        watchlist_id: str | None = None,
        limit: int = 50,
    ) -> list[RawPost]:
        """实现 Scraper Protocol: 按 keyword + 日期采集帖子。

        流程：
        1. search_feeds 获取帖子列表
        2. 从 post_id 前 8 位 hex 提取发布时间，过滤 target_date
        3. get_feed_detail 获取每条帖子的详情
        4. 解析为 RawPost 并落盘
        """
        self.manual_dir.mkdir(parents=True, exist_ok=True)

        # 1. 搜索帖子列表
        search_results = await self.search_feeds(keyword, limit=limit)
        if not search_results:
            logger.warning(f"[XhsMcpScraper] search_feeds returned empty for keyword={keyword!r}")
            return []

        # 2. 按日期过滤 (从 post_id 提取发布时间)
        target_posts = []
        for item in search_results:
            post_id = item.get("note_id") or item.get("id") or ""
            if not post_id:
                continue
            publish_date = _ms_to_cn_date(_post_id_to_unix_ms(post_id))
            if publish_date == target_date:
                target_posts.append(item)

        if not target_posts:
            logger.info(
                f"[XhsMcpScraper] No posts found for keyword={keyword!r} on {target_date}"
            )
            return []

        logger.info(
            f"[XhsMcpScraper] Found {len(target_posts)} posts for keyword={keyword!r} on {target_date}"
        )

        # 3. 获取详情并解析
        posts: list[RawPost] = []
        for item in target_posts:
            post_id = item.get("note_id") or item.get("id") or ""
            xsec_token = item.get("xsec_token") or item.get("xsecToken") or ""

            try:
                detail = await self.get_feed_detail(post_id, xsec_token)
            except Exception as e:
                logger.error(f"[XhsMcpScraper] get_feed_detail failed for {post_id}: {e}")
                continue

            # 落盘
            self._save_to_manual(detail, keyword, watchlist_id, post_id)

            # 解析为 RawPost
            try:
                # 添加 _meta 字段供 ManualScraper 使用
                detail["_meta"] = {
                    "keyword": keyword,
                    "watchlist_id": watchlist_id,
                    "xsec_token": xsec_token,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }
                post = parse_xhs_feed_detail(
                    detail,
                    keyword=keyword,
                    watchlist_id=watchlist_id,
                    xsec_token=xsec_token,
                )
                posts.append(post)
            except Exception as e:
                logger.error(f"[XhsMcpScraper] parse_xhs_feed_detail failed for {post_id}: {e}")
                continue

        return posts

    async def _mcp_call(self, method_name: str, arguments: dict, call_id: int = 2) -> dict:
        """发送 MCP 请求（含 initialize 握手），返回解析后的结果。

        MCP over HTTP 要求每次请求都先 initialize，用 JSON-RPC batch 实现。
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.mcp_url,
                json=[
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "clientInfo": {"name": "rednote-monitor", "version": "0.1"},
                        },
                    },
                    {
                        "jsonrpc": "2.0",
                        "id": call_id,
                        "method": "tools/call",
                        "params": {"name": method_name, "arguments": arguments},
                    },
                ],
            )
            response.raise_for_status()
            batch = response.json()

            for resp in batch:
                if resp.get("id") == call_id:
                    result = resp.get("result", {})
                    if result.get("isError"):
                        error_text = result["content"][0]["text"]
                        logger.error(f"[XhsMcp] {method_name} error: {error_text[:200]}")
                        return {}
                    content = result.get("content", [])
                    if content and isinstance(content[0], dict):
                        text = content[0].get("text", "")
                        if text:
                            try:
                                return json.loads(text)
                            except json.JSONDecodeError:
                                pass
            return {}

    async def search_feeds(self, keyword: str, limit: int = 50) -> list[dict]:
        """调用 MCP search_feeds 接口，返回帖子列表。

        v2 API 返回格式: {"feeds": [{"id": "...", "xsecToken": "...", "noteCard": {...}}]}
        兼容旧格式: [{"note_id": "...", "xsec_token": "...", "title": "..."}]
        """
        parsed = await self._mcp_call("search_feeds", {
            "keyword": keyword,
            "filters": {"sort_by": "最新"},
        })

        if not parsed:
            return []

        # v2 API: {"feeds": [...]}
        if isinstance(parsed, dict):
            feeds = parsed.get("feeds", [])
            return [
                {
                    "note_id": f.get("id", ""),
                    "xsec_token": f.get("xsecToken", ""),
                    "title": (f.get("noteCard") or {}).get("displayTitle", ""),
                }
                for f in feeds
            ]
        # 旧格式: [{"note_id": "...", ...}]
        if isinstance(parsed, list):
            return parsed

        return []

    async def get_feed_detail(self, post_id: str, xsec_token: str = "") -> dict:
        """调用 MCP get_feed_detail 接口，返回帖子详情。

        v2 API 参数: feed_id (非 note_id)。
        返回格式: {"feed_id": "...", "data": {"note": {...}, "comments": {"list": [...]}}}
        parse_xhs_feed_detail 已兼容此格式。
        """
        return await self._mcp_call("get_feed_detail", {
            "feed_id": post_id,
            "xsec_token": xsec_token,
        })

    def _save_to_manual(
        self,
        payload: dict,
        keyword: str,
        watchlist_id: str | None,
        post_id: str,
    ) -> Path:
        """落盘到 manual_dir，文件名格式与 ManualScraper 兼容。"""
        self.manual_dir.mkdir(parents=True, exist_ok=True)

        today = date.today().strftime("%Y%m%d")
        post_prefix = post_id[:8] if len(post_id) >= 8 else post_id
        filename = f"test_{today}_{watchlist_id or 'unknown'}_feed_{post_prefix}_detail.json"
        filepath = self.manual_dir / filename

        # 添加 _meta 字段
        payload["_meta"] = {
            "keyword": keyword,
            "watchlist_id": watchlist_id,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

        filepath.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info(f"[XhsMcpScraper] Saved detail to {filepath}")
        return filepath
