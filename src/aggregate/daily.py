"""每日指标聚合器"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlmodel import Session, SQLModel, create_engine, select

from ..models import DailyMetric, ScoredPost


class DailyAggregator:
    """每日指标聚合器

    将ScoredPost聚合为DailyMetric，存储到SQLite数据库
    """

    def __init__(self, db_path: str = "data/metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        SQLModel.metadata.create_all(self.engine)

    def aggregate(self, scored_posts: list[ScoredPost], date: Optional[datetime] = None) -> DailyMetric:
        """聚合ScoredPost为DailyMetric

        Args:
            scored_posts: 已评分的帖子列表
            date: 聚合日期，默认为今天

        Returns:
            DailyMetric: 聚合后的每日指标
        """
        if date is None:
            date = datetime.now()

        # 计算基础指标
        total_posts = len(scored_posts)
        relevant_posts = [p for p in scored_posts if p.is_relevant]
        relevant_count = len(relevant_posts)

        # 计算情绪指标
        if relevant_count > 0:
            sentiment_avg = sum(p.sentiment_score for p in relevant_posts) / relevant_count
            sentiment_comments_avg = sum(
                p.sentiment_comments_avg for p in relevant_posts
            ) / relevant_count
        else:
            sentiment_avg = 0.0
            sentiment_comments_avg = 0.0

        # 计算互动指标
        total_likes = sum(p.n_likes for p in scored_posts)
        total_comments = sum(p.n_comments for p in scored_posts)

        # 创建DailyMetric
        metric = DailyMetric(
            date=date.date(),
            stock_code=self._extract_stock_code(scored_posts),
            total_posts=total_posts,
            relevant_count=relevant_count,
            sentiment_avg=sentiment_avg,
            sentiment_comments_avg=sentiment_comments_avg,
            total_likes=total_likes,
            total_comments=total_comments,
        )

        # 存储到数据库
        self._save_metric(metric)

        return metric

    def _extract_stock_code(self, posts: list[ScoredPost]) -> str:
        """从帖子中提取股票代码"""
        # TODO: 实现股票代码提取逻辑
        return "UNKNOWN"

    def _save_metric(self, metric: DailyMetric) -> None:
        """保存指标到数据库"""
        with Session(self.engine) as session:
            session.add(metric)
            session.commit()

    def get_metric(self, date: datetime, stock_code: str) -> Optional[DailyMetric]:
        """获取指定日期的指标"""
        with Session(self.engine) as session:
            statement = select(DailyMetric).where(
                DailyMetric.date == date.date(),
                DailyMetric.stock_code == stock_code
            )
            result = session.exec(statement).first()
            return result
