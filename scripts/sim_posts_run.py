"""一次性模拟脚本:绕开 M1,直接造 5 个代表性 RawPost 喂 M2 + M3。

用法:set -a; source .env; set +a; uv run python scripts/sim_posts_run.py
观察:每个帖子的 ScoredPost 细节 + 1 行 DailyMetric。
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import date, datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")  # Windows 控制台默认 GBK,不重配会撞 emoji/中文

from src.m2_sentiment import SentimentEngine
from src.m3_aggregate import DailyAggregator
from src.models import RawComment, RawPost

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

NOW = datetime.now(timezone.utc)
PUBLISH_MS = int(NOW.timestamp() * 1000)
TODAY = date.today()


def mk_comments(items: list[tuple[str, int]]) -> list[RawComment]:
    """items = [(text, n_likes), ...]"""
    return [
        RawComment(comment_id=f"c{i:03d}", text=t, n_likes=likes)
        for i, (t, likes) in enumerate(items)
    ]


POSTS = [
    # 1) 强负面 + 恐慌
    RawPost(
        post_id="sim_001",
        keyword="甲骨文",
        watchlist_id="oracle",
        title="ORCL 被套了三个月,生活费都没了",
        desc="本来想搏一把改命,结果跌了 30%。每天看 K 线手都在抖。打算割肉了,这破公司没救了。",
        text="ORCL 被套了三个月,生活费都没了\n\n本来想搏一把改命,结果跌了 30%。每天看 K 线手都在抖。打算割肉了,这破公司没救了。",
        author_id="u1", author_nickname="韭菜本菜",
        n_likes=234, n_comments_total=5,
        publish_time_ms=PUBLISH_MS, publish_date=TODAY,
        fetched_at=NOW,
        comments=mk_comments([
            ("勇士,我也亏麻了", 45),
            ("跌了就是机会啊兄弟,加仓!", 12),
            ("我去年也是这么割的,然后股价翻了三倍 😅", 67),
            ("别割,云业务还在涨,熬熬就过去了", 23),
            ("散户的钱不是钱么", 8),
        ]),
    ),
    # 2) 强正面 + FOMO
    RawPost(
        post_id="sim_002",
        keyword="甲骨文",
        watchlist_id="oracle",
        title="梭哈 ORCL 一周翻倍!兄弟们冲啊",
        desc="财报超预期,云业务 +25%,我重仓全部 ORCL,这波直接财富自由。还没上车的赶紧,慢就来不及了!",
        text="梭哈 ORCL 一周翻倍!兄弟们冲啊\n\n财报超预期,云业务 +25%,我重仓全部 ORCL,这波直接财富自由。还没上车的赶紧,慢就来不及了!",
        author_id="u2", author_nickname="股神在线",
        n_likes=1245, n_comments_total=4,
        publish_time_ms=PUBLISH_MS, publish_date=TODAY,
        fetched_at=NOW,
        comments=mk_comments([
            ("已上车!", 89),
            ("现在追高是不是太晚了 🤔", 134),
            ("永远的神!", 56),
            ("接盘侠们辛苦了", 78),
        ]),
    ),
    # 3) 反讽(字面正向,语境讽刺)
    RawPost(
        post_id="sim_003",
        keyword="甲骨文",
        watchlist_id="oracle",
        title="ORCL 涨得真好,我们散户的钱真好赚",
        desc="每次我刚买就跌,刚卖就涨。这市场对散户真是太友好了 👍 主力资金的爸爸们辛苦了。",
        text="ORCL 涨得真好,我们散户的钱真好赚\n\n每次我刚买就跌,刚卖就涨。这市场对散户真是太友好了 👍 主力资金的爸爸们辛苦了。",
        author_id="u3", author_nickname="反向指标活体",
        n_likes=856, n_comments_total=4,
        publish_time_ms=PUBLISH_MS, publish_date=TODAY,
        fetched_at=NOW,
        comments=mk_comments([
            ("懂了,你买我卖", 234),
            ("把你的操作发我,我反着来", 178),
            ("散户之友 👍👍", 56),
            ("听君一席话,亏 50%", 89),
        ]),
    ),
    # 4) 无关帖(古文字甲骨文学习,不是股票)
    RawPost(
        post_id="sim_004",
        keyword="甲骨文",
        watchlist_id="oracle",
        title="甲骨文学习笔记 day 30",
        desc="今天临摹了 5 个甲骨文字符,'日''月''山''水''火'。商代的字真的好美,推荐买《甲骨文合集》入门。",
        text="甲骨文学习笔记 day 30\n\n今天临摹了 5 个甲骨文字符,'日''月''山''水''火'。商代的字真的好美,推荐买《甲骨文合集》入门。",
        author_id="u4", author_nickname="文字爱好者",
        n_likes=87, n_comments_total=3,
        publish_time_ms=PUBLISH_MS, publish_date=TODAY,
        fetched_at=NOW,
        comments=mk_comments([
            ("书法老师力荐!", 12),
            ("我也在学,加油 💪", 8),
            ("有没有线上课推荐", 5),
        ]),
    ),
    # 5) 理性分析
    RawPost(
        post_id="sim_005",
        keyword="甲骨文",
        watchlist_id="oracle",
        title="ORCL Q3 财报分析:云业务护城河 vs AI 投入风险",
        desc="云收入 +25% 是亮点,但 capex 也涨了 40%。短期估值已 price in 利好,中期看 AI 客户能不能 retain。我中性偏多。",
        text="ORCL Q3 财报分析:云业务护城河 vs AI 投入风险\n\n云收入 +25% 是亮点,但 capex 也涨了 40%。短期估值已 price in 利好,中期看 AI 客户能不能 retain。我中性偏多。",
        author_id="u5", author_nickname="二级狗",
        n_likes=345, n_comments_total=3,
        publish_time_ms=PUBLISH_MS, publish_date=TODAY,
        fetched_at=NOW,
        comments=mk_comments([
            ("分析得很扎实", 23),
            ("capex 这块同意,自由现金流要打折看", 18),
            ("中性偏多 = 不知道 😂", 45),
        ]),
    ),
]


def main():
    engine = SentimentEngine()  # 自动从 .env 读 LLM_BASE_URL / LLM_API_KEY / LLM_MODEL
    print(f"=== M2 SentimentEngine: model={engine.model}, base_url={engine.base_url} ===\n")

    scored_posts = []
    for i, post in enumerate(POSTS, 1):
        print(f"--- [{i}/{len(POSTS)}] {post.post_id} | author={post.author_nickname} ---")
        print(f"  text: {post.text[:60]}...")
        try:
            sp = engine.analyze(post)
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}\n")
            continue

        print(f"  is_relevant         = {sp.is_relevant}")
        print(f"  sentiment_post      = {sp.sentiment_post:+d}")
        print(f"  fomo                = {sp.fomo}")
        print(f"  quote               = {sp.quote!r}")
        print(f"  n_comments_scored   = {sp.n_comments_scored}")
        print(f"  sentiment_comments_avg = {sp.sentiment_comments_avg:+.3f}  (n_likes-weighted)")
        print(f"  sentiment_comments_std = {sp.sentiment_comments_std:.3f}")
        print(f"  cost                = ${sp.cost_usd:.4f}")
        # show per-comment scores summary
        cscores = [c.sentiment for c in sp.comment_scores if c.is_relevant]
        print(f"  comment_scores (relevant) = {cscores}")
        print()
        scored_posts.append(sp)

    print(f"=== M2 Total: {len(scored_posts)} scored, cost=${sum(sp.cost_usd for sp in scored_posts):.4f} ===\n")

    # M3
    print("--- M3 Aggregator ---")
    agg = DailyAggregator(db_path="data/sim.db")
    metric = agg.aggregate(scored_posts, target_date=TODAY)
    print(f"  date                = {metric.date}")
    print(f"  ticker              = {metric.ticker}")
    print(f"  n_posts (relevant)  = {metric.n_posts}")
    print(f"  sentiment_post_avg  = {metric.sentiment_post_avg:+.4f}")
    print(f"  sentiment_comment_avg = {metric.sentiment_comment_avg:+.4f}")
    print(f"  sentiment_combined  = {metric.sentiment_combined:+.4f}  ← 反指信号")
    print(f"  top_quotes          = {json.loads(metric.top_quotes_json)}")


if __name__ == "__main__":
    main()
