"""XhsMcpScraper 单元测试。

使用 pytest + pytest-asyncio 测试异步接口。
Mock _mcp_call 方法，避免依赖真实的 xiaohongshu-mcp 服务。
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.m1_scraper.xhs_mcp import XhsMcpScraper


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #


@pytest.fixture
def mock_mcp_url():
    return "http://127.0.0.1:18060/mcp"


@pytest.fixture
def tmp_manual_dir(tmp_path):
    return tmp_path / "manual"


@pytest.fixture
def scraper(mock_mcp_url, tmp_manual_dir):
    return XhsMcpScraper(mcp_url=mock_mcp_url, manual_dir=tmp_manual_dir)


@pytest.fixture
def sample_search_parsed():
    """search_feeds 解析后的返回 (v2 API)。"""
    return {
        "feeds": [
            {
                "id": "6823a1b400000000010001",
                "xsecToken": "abc123",
                "noteCard": {
                    "displayTitle": "甲骨文 ORCL 财报超预期",
                    "type": "normal",
                },
            },
            {
                "id": "6823a1b400000000010002",
                "xsecToken": "def456",
                "noteCard": {
                    "displayTitle": "甲骨文云业务增长",
                    "type": "normal",
                },
            },
        ]
    }


@pytest.fixture
def sample_detail_parsed():
    """get_feed_detail 解析后的返回 (v2 API)。"""
    return {
        "feed_id": "6823a1b400000000010001",
        "data": {
            "note": {
                "noteId": "6823a1b400000000010001",
                "title": "甲骨文 ORCL 财报超预期",
                "desc": "今日甲骨文发布财报...",
                "type": "normal",
                "user": {
                    "userId": "user001",
                    "nickname": "投资达人",
                },
                "interactInfo": {
                    "likedCount": "234",
                    "commentCount": "87",
                    "collectedCount": "56",
                    "sharedCount": "12",
                },
                "time": 1747104000000,
                "ipLocation": "上海",
            },
            "comments": {
                "list": [
                    {
                        "id": "c1",
                        "content": "看好甲骨文",
                        "likeCount": "12",
                        "userInfo": {
                            "userId": "user002",
                            "nickname": "小散",
                        },
                    },
                    {
                        "id": "c2",
                        "content": "已经上车了",
                        "likeCount": "5",
                        "userInfo": {
                            "userId": "user003",
                            "nickname": "韭菜",
                        },
                    },
                ]
            },
        },
    }


# ------------------------------------------------------------------ #
# Tests: search_feeds
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_search_feeds(scraper, sample_search_parsed):
    """测试 search_feeds 接口调用。"""
    with patch.object(scraper, "_mcp_call", new_callable=AsyncMock, return_value=sample_search_parsed):
        results = await scraper.search_feeds("甲骨文", limit=10)

    assert len(results) == 2
    assert results[0]["note_id"] == "6823a1b400000000010001"
    assert results[0]["xsec_token"] == "abc123"
    assert results[1]["note_id"] == "6823a1b400000000010002"


@pytest.mark.asyncio
async def test_search_feeds_empty(scraper):
    """测试 search_feeds 返回空结果。"""
    with patch.object(scraper, "_mcp_call", new_callable=AsyncMock, return_value={}):
        results = await scraper.search_feeds("不存在的关键词")

    assert results == []


# ------------------------------------------------------------------ #
# Tests: get_feed_detail
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_get_feed_detail(scraper, sample_detail_parsed):
    """测试 get_feed_detail 接口调用。"""
    with patch.object(scraper, "_mcp_call", new_callable=AsyncMock, return_value=sample_detail_parsed):
        detail = await scraper.get_feed_detail("6823a1b400000000010001", "abc123")

    assert "data" in detail
    assert detail["data"]["note"]["noteId"] == "6823a1b400000000010001"
    assert "comments" in detail["data"]


# ------------------------------------------------------------------ #
# Tests: fetch (完整流程)
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_fetch_by_date(scraper, sample_search_parsed, sample_detail_parsed, tmp_manual_dir):
    """测试按日期过滤帖子。"""
    # post_id "6823a1b400000000010001" -> 前 8 位 hex "6823a1b4" -> unix 秒 1747165620
    # 1747165620 秒 = 2025-05-13 17:07 UTC -> 2025-05-14 01:07 UTC+8

    with patch.object(scraper, "_mcp_call", new_callable=AsyncMock) as mock_call:
        # 第一次调用是 search_feeds，第二次是 get_feed_detail
        mock_call.side_effect = [sample_search_parsed, sample_detail_parsed]

        # 目标日期 = 2025-05-14 (从 post_id 推算，UTC+8)
        posts = await scraper.fetch("甲骨文", date(2025, 5, 14))

    assert len(posts) == 1
    assert posts[0].post_id == "6823a1b400000000010001"
    assert posts[0].keyword == "甲骨文"
    assert posts[0].title == "甲骨文 ORCL 财报超预期"
    assert len(posts[0].comments) == 2

    # 验证落盘
    assert tmp_manual_dir.exists()
    files = list(tmp_manual_dir.glob("*_detail.json"))
    assert len(files) == 1


@pytest.mark.asyncio
async def test_fetch_no_matching_date(scraper, sample_search_parsed):
    """测试目标日期无匹配帖子。"""
    with patch.object(scraper, "_mcp_call", new_callable=AsyncMock, return_value=sample_search_parsed):
        # 目标日期 = 2099-01-01，不会有匹配
        posts = await scraper.fetch("甲骨文", date(2099, 1, 1))

    assert posts == []


@pytest.mark.asyncio
async def test_fetch_mcp_unavailable(scraper):
    """测试 MCP 服务不可用时抛出异常。"""
    with patch.object(scraper, "_mcp_call", new_callable=AsyncMock, side_effect=Exception("Connection refused")):
        with pytest.raises(Exception, match="Connection refused"):
            await scraper.fetch("甲骨文", date(2025, 5, 13))


# ------------------------------------------------------------------ #
# Tests: _save_to_manual
# ------------------------------------------------------------------ #


def test_save_to_manual(scraper, tmp_manual_dir):
    """测试落盘逻辑。"""
    payload = {
        "note": {
            "noteId": "6823a1b400000000010001",
            "title": "测试帖子",
        },
        "comments": [],
    }

    filepath = scraper._save_to_manual(payload, "甲骨文", "oracle", "6823a1b400000000010001")

    today = date.today().strftime("%Y%m%d")
    assert filepath.exists()
    assert filepath.name == f"test_{today}_oracle_feed_6823a1b4_detail.json"

    # 验证内容
    saved = json.loads(filepath.read_text(encoding="utf-8"))
    assert saved["_meta"]["keyword"] == "甲骨文"
    assert saved["_meta"]["watchlist_id"] == "oracle"
    assert "fetched_at" in saved["_meta"]


# ------------------------------------------------------------------ #
# Tests: FallbackScraper
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_fallback_to_manual(tmp_path):
    """测试降级到 ManualScraper。"""
    from src.m1_scraper.manual import ManualScraper
    from src.m1_scraper.fallback import FallbackScraper
    from src.m1_scraper.xhs_mcp import XhsMcpScraper

    manual_dir = tmp_path / "manual"
    manual_dir.mkdir()

    # 创建一个 mock detail 文件
    mock_detail = {
        "_meta": {
            "keyword": "甲骨文",
            "watchlist_id": "oracle",
            "fetched_at": "2026-05-13T10:00:00+00:00",
        },
        "note": {
            "noteId": "6823a1b400000000010001",
            "title": "手动采集的帖子",
            "desc": "测试内容",
            "type": "normal",
            "user": {"userId": "user001", "nickname": "测试用户"},
            "interactInfo": {"likedCount": "100", "commentCount": "20"},
            "time": 1747104000000,
        },
        "comments": [],
    }
    (manual_dir / "test_20260513_oracle_feed_6823a1b4_detail.json").write_text(
        json.dumps(mock_detail, ensure_ascii=False), encoding="utf-8"
    )

    primary = XhsMcpScraper(mcp_url="http://invalid:9999/mcp", manual_dir=manual_dir)
    fallback = ManualScraper(manual_dir=manual_dir)
    scraper = FallbackScraper(primary, fallback)

    # primary 会失败，应该降级到 fallback
    posts = await scraper.fetch("甲骨文", date(2025, 5, 13))

    assert len(posts) == 1
    assert posts[0].post_id == "6823a1b400000000010001"
    assert posts[0].title == "手动采集的帖子"
