"""M3 聚合模块单元测试。"""

from __future__ import annotations

import json
from datetime import date

import pytest

from src.m3_aggregate.daily import DailyAggregator
from src.models import CommentScore, ScoredPost


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #


@pytest.fixture
def aggregator(tmp_path):
    """创建测试用聚合器,使用临时目录避免污染项目。"""
    return DailyAggregator(db_path=str(tmp_path / "test_metrics.db"))


@pytest.fixture
def sample_scored_posts():
    """创建测试用 ScoredPost 列表。"""
    return [
        ScoredPost(
            post_id="post1",
            keyword="甲骨文",
            watchlist_id="oracle",
            date=date(2025, 5, 13),
            is_relevant=True,
            sentiment_post=2,
            comment_scores=[
                CommentScore(comment_id="c1", sentiment=1, is_relevant=True),
            ],
            n_comments_scored=1,
            sentiment_comments_avg=1.0,
            sentiment_comments_std=0.0,
            fomo=7,
            quote="云业务收入同比增长25%",
            model="mimo-v2.5-pro",
            cost_usd=0.001,
        ),
        ScoredPost(
            post_id="post2",
            keyword="甲骨文",
            watchlist_id="oracle",
            date=date(2025, 5, 13),
            is_relevant=True,
            sentiment_post=-1,
            comment_scores=[],
            n_comments_scored=0,
            sentiment_comments_avg=0.0,
            sentiment_comments_std=0.0,
            fomo=0,
            quote="股价暴跌",
            model="mimo-v2.5-pro",
            cost_usd=0.001,
        ),
        ScoredPost(
            post_id="post3",
            keyword="甲骨文",
            watchlist_id="oracle",
            date=date(2025, 5, 13),
            is_relevant=False,  # 不相关,应被排除
            sentiment_post=0,
            comment_scores=[],
            n_comments_scored=0,
            sentiment_comments_avg=0.0,
            sentiment_comments_std=0.0,
            fomo=0,
            quote="甲骨文是古代文字",
            model="mimo-v2.5-pro",
            cost_usd=0.001,
        ),
    ]


# ------------------------------------------------------------------ #
# Tests
# ------------------------------------------------------------------ #


class TestDailyAggregator:
    def test_aggregate_basic(self, aggregator, sample_scored_posts):
        """基本聚合: 只统计 is_relevant=true 的帖子。"""
        metric = aggregator.aggregate(sample_scored_posts)

        assert metric.ticker == "oracle"
        assert metric.n_posts == 2  # post3 is_relevant=false 被排除
        assert metric.date == date(2025, 5, 13)

        # post_avg = (2 + -1) / 2 = 0.5
        assert abs(metric.sentiment_post_avg - 0.5) < 0.01

        # comment_avg = (1.0 + 0.0) / 2 = 0.5
        assert abs(metric.sentiment_comment_avg - 0.5) < 0.01

        # combined = 0.6 * 0.5 + 0.4 * 0.5 = 0.5
        assert abs(metric.sentiment_combined - 0.5) < 0.01

        # top_quotes 包含 relevant 帖子的 quote
        quotes = json.loads(metric.top_quotes_json)
        assert "云业务收入同比增长25%" in quotes
        assert "股价暴跌" in quotes

    def test_aggregate_empty_list(self, aggregator):
        """空列表聚合返回默认值。"""
        metric = aggregator.aggregate([])

        assert metric.ticker == "UNKNOWN"
        assert metric.n_posts == 0
        assert metric.sentiment_post_avg == 0.0
        assert metric.sentiment_comment_avg == 0.0
        assert metric.sentiment_combined == 0.0
        assert json.loads(metric.top_quotes_json) == []

    def test_aggregate_with_date(self, aggregator, sample_scored_posts):
        """指定日期聚合。"""
        test_date = date(2024, 1, 15)
        metric = aggregator.aggregate(sample_scored_posts, target_date=test_date)

        assert metric.date == test_date

    def test_aggregate_all_irrelevant(self, aggregator):
        """所有帖子都不相关时,n_posts=0。"""
        posts = [
            ScoredPost(
                post_id="p1",
                keyword="test",
                watchlist_id="test",
                date=date(2025, 1, 1),
                is_relevant=False,
                sentiment_post=0,
                model="test",
            ),
        ]
        metric = aggregator.aggregate(posts)

        assert metric.n_posts == 0
        assert metric.sentiment_post_avg == 0.0

    def test_save_and_retrieve(self, aggregator, sample_scored_posts):
        """保存后能从数据库检索。"""
        aggregator.aggregate(sample_scored_posts)

        result = aggregator.get_metric(date(2025, 5, 13), "oracle")
        assert result is not None
        assert result.n_posts == 2
        assert result.ticker == "oracle"

    def test_get_nonexistent_metric(self, aggregator):
        """查询不存在的指标返回 None。"""
        result = aggregator.get_metric(date(2099, 1, 1), "nonexistent")
        assert result is None
