"""M3聚合模块测试"""

import pytest
from datetime import datetime

from src.aggregate import DailyAggregator
from src.models import ScoredPost


@pytest.fixture
def aggregator():
    """创建测试用聚合器"""
    return DailyAggregator(db_path="data/test_metrics.db")


@pytest.fixture
def sample_scored_posts():
    """创建测试用ScoredPost列表"""
    return [
        ScoredPost(
            post_id="test1",
            stock_code="AAPL",
            content="苹果股票表现不错",
            sentiment_score=0.8,
            is_relevant=True,
            n_likes=100,
            n_comments=20,
            sentiment_comments_avg=0.7,
        ),
        ScoredPost(
            post_id="test2",
            stock_code="AAPL",
            content="苹果股票要跌了",
            sentiment_score=-0.5,
            is_relevant=True,
            n_likes=50,
            n_comments=10,
            sentiment_comments_avg=-0.3,
        ),
    ]


def test_aggregate_basic(aggregator, sample_scored_posts):
    """测试基本聚合功能"""
    metric = aggregator.aggregate(sample_scored_posts)

    assert metric.total_posts == 2
    assert metric.relevant_count == 2
    assert metric.stock_code == "AAPL"
    assert metric.total_likes == 150
    assert metric.total_comments == 30


def test_aggregate_empty_list(aggregator):
    """测试空列表聚合"""
    metric = aggregator.aggregate([])

    assert metric.total_posts == 0
    assert metric.relevant_count == 0
    assert metric.sentiment_avg == 0.0


def test_aggregate_with_date(aggregator, sample_scored_posts):
    """测试指定日期聚合"""
    test_date = datetime(2024, 1, 15)
    metric = aggregator.aggregate(sample_scored_posts, date=test_date)

    assert metric.date == test_date.date()
