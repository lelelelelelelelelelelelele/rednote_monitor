"""KeywordMonitor — keyword 噪声率监控。

BLUEPRINT § 四.A KPI:
    keyword 噪声率监控: 对每个 watchlist 跟踪 M2 标的 is_relevant=false 比例, >50% 就要调 keyword

使用方式:
    monitor = KeywordMonitor(threshold=0.5)
    monitor.update("甲骨文", is_relevant=True)
    monitor.update("甲骨文", is_relevant=False)
    noise_rate = monitor.get_noise_rate("甲骨文")  # 0.5
    alerts = monitor.check_and_alert()  # ["甲骨文"] if noise_rate > threshold
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class KeywordStats:
    """单个 keyword 的统计信息。"""

    total: int = 0
    irrelevant: int = 0

    @property
    def noise_rate(self) -> float:
        """噪声率 = irrelevant / total。"""
        if self.total == 0:
            return 0.0
        return self.irrelevant / self.total


class KeywordMonitor:
    """监控 keyword 的噪声率 (is_relevant=false 比例)。

    当噪声率超过阈值时，说明该 keyword 召回了太多非投资语料，
    需要调整 keyword 或增加过滤。
    """

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.stats: dict[str, KeywordStats] = {}

    def update(self, keyword: str, is_relevant: bool) -> None:
        """更新统计。M2 每处理一条帖子后调用。"""
        if keyword not in self.stats:
            self.stats[keyword] = KeywordStats()

        self.stats[keyword].total += 1
        if not is_relevant:
            self.stats[keyword].irrelevant += 1

    def get_noise_rate(self, keyword: str) -> float:
        """获取指定 keyword 的噪声率。"""
        if keyword not in self.stats:
            return 0.0
        return self.stats[keyword].noise_rate

    def get_stats(self, keyword: str) -> KeywordStats:
        """获取指定 keyword 的统计信息。"""
        return self.stats.get(keyword, KeywordStats())

    def check_and_alert(self) -> list[str]:
        """检查所有 keyword，返回超标的 keyword 列表。

        超标条件: noise_rate > threshold
        """
        alerts: list[str] = []
        for keyword, stats in self.stats.items():
            if stats.total > 0 and stats.noise_rate > self.threshold:
                alerts.append(keyword)
                logger.warning(
                    f"[KeywordMonitor] ALERT: keyword={keyword!r} "
                    f"noise_rate={stats.noise_rate:.1%} ({stats.irrelevant}/{stats.total}) "
                    f"exceeds threshold {self.threshold:.1%}. Consider adjusting keyword."
                )
        return alerts

    def reset(self, keyword: str | None = None) -> None:
        """重置统计。不传 keyword 则重置所有。"""
        if keyword:
            self.stats.pop(keyword, None)
        else:
            self.stats.clear()

    def summary(self) -> str:
        """返回所有 keyword 的统计摘要。"""
        lines = ["Keyword Noise Rate Summary:", f"  Threshold: {self.threshold:.1%}", ""]
        for keyword, stats in sorted(self.stats.items()):
            status = "ALERT" if stats.noise_rate > self.threshold else "OK"
            lines.append(
                f"  [{status}] {keyword}: {stats.noise_rate:.1%} "
                f"({stats.irrelevant}/{stats.total})"
            )
        return "\n".join(lines)
