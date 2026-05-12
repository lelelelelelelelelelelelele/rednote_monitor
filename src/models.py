"""rednote_monitor 数据契约 — 多人协作高频冲突点,改字段前群里 +1。

字段对齐 BLUEPRINT.md § 三,在此基础上保留 XHS 原始抓回的若干上下文字段
(ip_location / collected / xsec_token / parent_comment_id 等),不强制 M2 使用,
但 M2 想用时不用回头改 M1。
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# ------------------------------------------------------------------ #
# M1 输出 (Scraper → Sentiment)
# ------------------------------------------------------------------ #


class RawComment(BaseModel):
    """一条评论或子评论。BLUEPRINT 只要求 {text, n_likes},此处扩展为可分级、可溯源的形式。"""

    comment_id: str
    text: str
    n_likes: int = 0
    author_id: str | None = None
    author_nickname: str | None = None
    ip_location: str | None = None
    ts_ms: int | None = None
    parent_comment_id: str | None = None  # None = 一级评论
    is_post_author: bool = False           # 楼主回复自家帖时为 True


class RawPost(BaseModel):
    """单条小红书帖子 + 其评论。

    `text` = title + "\\n\\n" + desc,供 LLM 直接吃。原始 title/desc 也独立保留。
    BLUEPRINT 的 `date` 在这里是 publish_date (UTC+8 本地日期),由 publish_time_ms 推。
    """

    post_id: str
    keyword: str                            # watchlist 命中的 keyword
    watchlist_id: str | None = None         # watchlist.yaml 里的 id,M3 用

    title: str = ""
    desc: str = ""
    text: str = ""                          # 合成: title + \n\n + desc

    note_type: Literal["normal", "video", "unknown"] = "normal"

    author_id: str
    author_nickname: str

    image_urls: list[str] = Field(default_factory=list)

    n_likes: int = 0
    n_comments_total: int = 0
    n_collected: int = 0
    n_shared: int = 0

    ip_location: str | None = None
    publish_time_ms: int                    # XHS 原始毫秒时间戳
    publish_date: date                      # UTC+8 当地日期

    comments: list[RawComment] = Field(default_factory=list)

    xsec_token: str | None = None           # 重抓需要

    fetched_at: datetime                    # 抓取时间,便于回溯 cookie 失效之类的问题

    @field_validator("note_type", mode="before")
    @classmethod
    def _normalize_note_type(cls, v: Any) -> str:
        if v in ("normal", "video"):
            return v
        return "unknown"


# ------------------------------------------------------------------ #
# M2 输出 (Sentiment → Aggregator)
# ------------------------------------------------------------------ #


SentimentScore = Literal[-2, -1, 0, 1, 2]


class CommentScore(BaseModel):
    """单条评论的 M2 打分结果。M2 用方案 B(单帖批量喂)时填充。"""

    comment_id: str
    sentiment: SentimentScore
    is_relevant: bool = True


class ScoredPost(BaseModel):
    """单帖打分结果。post / comments 分开打,严格遵守 BLUEPRINT 第 7 条决策。

    关键原则:**LLM 只判每条评论的 sentiment + relevance,不直接给评论区整体值**。
    `sentiment_comments_avg` 是 M2 后处理在 `comment_scores` 上按 `n_likes` 加权得到的连续值,
    保留分布信号(方差、bull/bear 占比)给 M3 聚合用。LLM 离散输出 + 客户端加权聚合,
    是为了避免一次直接给整体值时把 38 条评论的分布压成一个 5 档枚举。
    """

    post_id: str
    keyword: str
    watchlist_id: str | None = None
    date: date

    is_relevant: bool = True                 # 帖子整体是否与 watchlist 相关 (噪声门控)
    sentiment_post: SentimentScore           # 帖子主体 LLM 打分,离散 -2..+2

    # 评论区:LLM 只给 per-comment,M2 后处理算 avg
    comment_scores: list[CommentScore] = Field(default_factory=list)
    n_comments_scored: int = 0               # = len([c for c in comment_scores if c.is_relevant])
    sentiment_comments_avg: float = 0.0      # n_likes 加权,落在 [-2.0, +2.0]
    sentiment_comments_std: float = 0.0      # 方差,可选,M3 用

    fomo: int = Field(0, ge=0, le=10)        # 0-10 的 FOMO 分,可选指标

    quote: str = ""                          # 最具代表性的原句,供人工审计
    model: str                               # e.g. "gpt-4o-mini"
    cost_usd: float = 0.0


# ------------------------------------------------------------------ #
# M3 输出 (Aggregator → SQLite)
# ------------------------------------------------------------------ #


class DailyMetric(BaseModel):
    """一天 × 一个 watchlist_id 的聚合结果。表 daily_metrics 一行。"""

    ticker: str                              # watchlist_id (e.g. "oracle")
    date: date
    n_posts: int

    sentiment_post_avg: float
    sentiment_comment_avg: float
    sentiment_combined: float                # 0.6 * post_avg + 0.4 * comment_avg

    top_quotes_json: str                     # JSON-encoded list[str],3-5 条


# ------------------------------------------------------------------ #
# XHS → RawPost 解析适配器
# ------------------------------------------------------------------ #


def _ms_to_cn_date(ms: int) -> date:
    """毫秒时间戳 → 北京时间(UTC+8)的日期。XHS publish_time 是 epoch ms。"""
    from datetime import timedelta
    return (datetime.fromtimestamp(ms / 1000, tz=timezone.utc) + timedelta(hours=8)).date()


def _parse_count(v: Any) -> int:
    """XHS 的 likedCount/commentCount 是 string,可能是空串或 '1.2万'。空串 → 0。"""
    if v is None or v == "":
        return 0
    if isinstance(v, int):
        return v
    s = str(v)
    if s.endswith("万"):
        try:
            return int(float(s[:-1]) * 10000)
        except ValueError:
            return 0
    try:
        return int(s)
    except ValueError:
        return 0


def parse_xhs_feed_detail(
    payload: dict,
    keyword: str,
    watchlist_id: str | None = None,
    xsec_token: str | None = None,
    fetched_at: datetime | None = None,
) -> RawPost:
    """把 mcp__xiaohongshu__get_feed_detail 的返回(可能套了一层 _meta + data)解析成 RawPost。

    支持两种 payload 形态:
      1. {"data": {"note": {...}, "comments": {"list": [...]}}}       — MCP 原始返回
      2. {"note": {...}, "comments": [...]}                            — 我们落盘的精简版
    """
    note_dict, comments_list = _extract_note_and_comments(payload)

    post_id = note_dict.get("noteId") or note_dict.get("post_id") or ""
    title = note_dict.get("title", "") or ""
    desc = note_dict.get("desc", "") or ""
    text = (title + "\n\n" + desc).strip() if (title or desc) else ""

    user = note_dict.get("user", {})
    author_id = user.get("userId", "") or ""
    author_nickname = user.get("nickname") or user.get("nickName") or ""

    interact = note_dict.get("interactInfo", {}) or note_dict.get("interact", {})
    n_likes = _parse_count(interact.get("likedCount") or interact.get("liked_count"))
    n_comments_total = _parse_count(interact.get("commentCount") or interact.get("comment_count"))
    n_collected = _parse_count(interact.get("collectedCount") or interact.get("collected_count"))
    n_shared = _parse_count(interact.get("sharedCount") or interact.get("shared_count"))

    image_urls = _extract_image_urls(note_dict)

    publish_time_ms = note_dict.get("time") or note_dict.get("publish_time_ms")
    if publish_time_ms is None and post_id:
        publish_time_ms = _post_id_to_unix_ms(post_id)
    publish_time_ms = int(publish_time_ms or 0)

    raw_note_type = note_dict.get("type", "normal")
    comments = _parse_comments(comments_list, post_author_id=author_id)

    return RawPost(
        post_id=post_id,
        keyword=keyword,
        watchlist_id=watchlist_id,
        title=title,
        desc=desc,
        text=text,
        note_type=raw_note_type,
        author_id=author_id,
        author_nickname=author_nickname,
        image_urls=image_urls,
        n_likes=n_likes,
        n_comments_total=n_comments_total,
        n_collected=n_collected,
        n_shared=n_shared,
        ip_location=note_dict.get("ipLocation") or note_dict.get("ip_location") or None,
        publish_time_ms=publish_time_ms,
        publish_date=_ms_to_cn_date(publish_time_ms) if publish_time_ms else date.today(),
        comments=comments,
        xsec_token=xsec_token or note_dict.get("xsecToken") or note_dict.get("xsec_token"),
        fetched_at=fetched_at or datetime.now(timezone.utc),
    )


def _post_id_to_unix_ms(post_id: str) -> int:
    """feed_id 前 8 个 hex char = unix 秒级时间戳(经验值,见 A 任务调查)。"""
    if len(post_id) < 8:
        return 0
    try:
        return int(post_id[:8], 16) * 1000
    except ValueError:
        return 0


def _extract_note_and_comments(payload: dict) -> tuple[dict, list]:
    """适配两种 payload 形态。"""
    if "data" in payload and isinstance(payload["data"], dict):
        data = payload["data"]
        note = data.get("note", {})
        comments = (data.get("comments", {}) or {}).get("list", [])
        return note, comments

    note = payload.get("note", {})
    comments = payload.get("comments", [])
    if isinstance(comments, dict):
        comments = comments.get("list", [])
    return note, comments


def _extract_image_urls(note_dict: dict) -> list[str]:
    if "image_urls" in note_dict:
        return list(note_dict["image_urls"])
    image_list = note_dict.get("imageList") or []
    urls: list[str] = []
    for img in image_list:
        url = img.get("urlDefault") or img.get("url") or img.get("urlPre")
        if url:
            urls.append(url)
    return urls


def _parse_comments(raw_list: list, post_author_id: str) -> list[RawComment]:
    """递归把 XHS 嵌套的 list+subComments 拍平成 list[RawComment](保留 parent_comment_id)。"""
    out: list[RawComment] = []

    for c in raw_list or []:
        if not isinstance(c, dict):
            continue
        cid = c.get("id", "")
        # XHS 原始返回 userInfo 是 dict;我们落盘的精简版可能直接给 user="某昵称"
        user_info = c.get("userInfo") if isinstance(c.get("userInfo"), dict) else None
        if user_info is None and isinstance(c.get("user"), dict):
            user_info = c["user"]
        user_info = user_info or {}
        nickname_from_str = c.get("user") if isinstance(c.get("user"), str) else None
        author_id = user_info.get("userId") or c.get("author_id") or None

        comment = RawComment(
            comment_id=cid,
            text=c.get("content") or c.get("text") or "",
            n_likes=_parse_count(c.get("likeCount") or c.get("n_likes") or c.get("likes")),
            author_id=author_id,
            author_nickname=user_info.get("nickname") or user_info.get("nickName") or nickname_from_str or None,
            ip_location=c.get("ipLocation") or c.get("ip") or None,
            ts_ms=c.get("createTime") or c.get("ts_ms"),
            parent_comment_id=None,
            is_post_author=(author_id is not None and author_id == post_author_id),
        )
        out.append(comment)

        for sub in c.get("subComments") or c.get("sub_sample") or []:
            if not isinstance(sub, dict):
                continue
            sub_user = sub.get("userInfo") if isinstance(sub.get("userInfo"), dict) else None
            if sub_user is None and isinstance(sub.get("user"), dict):
                sub_user = sub["user"]
            sub_user = sub_user or {}
            sub_nickname_from_str = sub.get("user") if isinstance(sub.get("user"), str) else None
            sub_author_id = sub_user.get("userId") or None
            out.append(
                RawComment(
                    comment_id=sub.get("id", f"{cid}-sub"),
                    text=sub.get("content") or sub.get("text") or "",
                    n_likes=_parse_count(sub.get("likeCount") or sub.get("likes")),
                    author_id=sub_author_id,
                    author_nickname=sub_user.get("nickname") or sub_nickname_from_str or None,
                    ip_location=sub.get("ipLocation") or sub.get("ip") or None,
                    ts_ms=sub.get("createTime"),
                    parent_comment_id=cid,
                    is_post_author=(sub_author_id is not None and sub_author_id == post_author_id)
                    or bool(sub.get("is_author")),
                )
            )

    return out
