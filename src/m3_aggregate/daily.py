"""M3 Aggregator — 每日指标聚合模块。

BLUEPRINT § M3:
    把每日 N 条帖子的 ScoredPost → 一条 DailyMetric,写入 SQLite
    聚合规则:
    - sentiment_post_avg: 简单算术均值 (ScoredPost 无 n_likes 字段)
    - sentiment_comment_avg: 简单算术均值
    - sentiment_combined: 0.6 * post_avg + 0.4 * comment_avg
    - top_quotes: 挑 3-5 条信息量最大的引用
    - 只 count is_relevant=true 的帖子进 n_posts
"""

from __future__ import annotations

import json
from datetime import date as Date
from pathlib import Path
from typing import Optional

from sqlalchemy import Column, String, Integer, Float, Date as SACDate
from sqlalchemy.orm import declarative_base
from sqlmodel import Session, create_engine, select

from ..models import DailyMetric, ScoredPost

Base = declarative_base()


class DailyMetricRow(Base):
    """SQLite 表模型 — 对应 DailyMetric 数据契约。"""

    __tablename__ = "daily_metrics"

    ticker = Column(String, primary_key=True)
    date = Column(SACDate, primary_key=True)
    n_posts = Column(Integer, default=0)
    sentiment_post_avg = Column(Float, default=0.0)
    sentiment_comment_avg = Column(Float, default=0.0)
    sentiment_combined = Column(Float, default=0.0)
    top_quotes_json = Column(String, default="[]")


class DailyAggregator:
    """每日指标聚合器 — 将 ScoredPost 聚合为 DailyMetric,存储到 SQLite。"""

    def __init__(self, db_path: str = "data/metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)

    def aggregate(
        self,
        scored_posts: list[ScoredPost],
        target_date: Optional[Date] = None,
    ) -> DailyMetric:
        """聚合 ScoredPost 列表为一条 DailyMetric。

        Args:
            scored_posts: 已打分的帖子列表
            target_date: 聚合日期,默认取帖子的 date 字段

        Returns:
            DailyMetric: 聚合后的每日指标
        """
        if not scored_posts:
            return DailyMetric(
                ticker="UNKNOWN",
                date=target_date or Date.today(),
                n_posts=0,
                sentiment_post_avg=0.0,
                sentiment_comment_avg=0.0,
                sentiment_combined=0.0,
                top_quotes_json="[]",
            )

        # 从第一个帖子获取 ticker (watchlist_id)
        ticker = scored_posts[0].watchlist_id or "UNKNOWN"
        if target_date is None:
            target_date = scored_posts[0].date

        # 只统计 is_relevant=true 的帖子
        relevant = [p for p in scored_posts if p.is_relevant]
        n_posts = len(relevant)

        # 计算情绪指标
        if n_posts > 0:
            sentiment_post_avg = sum(p.sentiment_post for p in relevant) / n_posts
            sentiment_comment_avg = sum(p.sentiment_comments_avg for p in relevant) / n_posts
        else:
            sentiment_post_avg = 0.0
            sentiment_comment_avg = 0.0

        # 0.6 * post + 0.4 * comment
        sentiment_combined = 0.6 * sentiment_post_avg + 0.4 * sentiment_comment_avg

        # 挑 3-5 条 quote
        quotes = [p.quote for p in relevant if p.quote]
        top_quotes = quotes[:5]

        metric = DailyMetric(
            ticker=ticker,
            date=target_date,
            n_posts=n_posts,
            sentiment_post_avg=round(sentiment_post_avg, 4),
            sentiment_comment_avg=round(sentiment_comment_avg, 4),
            sentiment_combined=round(sentiment_combined, 4),
            top_quotes_json=json.dumps(top_quotes, ensure_ascii=False),
        )

        # 存储到数据库
        self._save_metric(metric)

        return metric

    def _save_metric(self, metric: DailyMetric) -> None:
        """保存指标到数据库 (转换为 SQLAlchemy 行)。"""
        row = DailyMetricRow(
            ticker=metric.ticker,
            date=metric.date,
            n_posts=metric.n_posts,
            sentiment_post_avg=metric.sentiment_post_avg,
            sentiment_comment_avg=metric.sentiment_comment_avg,
            sentiment_combined=metric.sentiment_combined,
            top_quotes_json=metric.top_quotes_json,
        )
        with Session(self.engine) as session:
            # Upsert: 先删除旧记录再插入
            existing = session.exec(
                select(DailyMetricRow).where(
                    DailyMetricRow.ticker == row.ticker,
                    DailyMetricRow.date == row.date,
                )
            ).first()
            if existing:
                session.delete(existing)
            session.add(row)
            session.commit()

    def get_metric(self, target_date: Date, ticker: str) -> Optional[DailyMetric]:
        """获取指定日期和 ticker 的指标"""
        with Session(self.engine) as session:
            statement = select(DailyMetricRow).where(
                DailyMetricRow.date == target_date,
                DailyMetricRow.ticker == ticker,
            )
            row = session.exec(statement).first()
            if row is None:
                return None
            return DailyMetric(
                ticker=row.ticker,
                date=row.date,
                n_posts=row.n_posts,
                sentiment_post_avg=row.sentiment_post_avg,
                sentiment_comment_avg=row.sentiment_comment_avg,
                sentiment_combined=row.sentiment_combined,
                top_quotes_json=row.top_quotes_json,
            )
