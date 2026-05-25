"""Quick script to test MiMo-v2.5-pro API via Token Plan.

Usage: Set LLM_API_KEY in .env file before running.
"""

import os
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# Load .env file
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

if not os.environ.get("LLM_API_KEY"):
    print("ERROR: LLM_API_KEY not set. Please create .env file with your API key.")
    sys.exit(1)

import httpx
from src.m2_sentiment.engine import SentimentEngine, _strip_markdown_fences
from src.models import RawPost, RawComment
from datetime import date, datetime, timezone

# === 1) Raw comment batch debug ===

print("=" * 60)
print("TEST 1: Raw comment batch LLM response")
print("=" * 60)

engine = SentimentEngine()
system, user = engine.prompts.render_comment_batch(
    keyword="甲骨文",
    post_text="甲骨文财报超预期。今日甲骨文发布财报，云业务收入同比增长25%。",
    comments=[
        {"comment_id": "c1", "text": "看好甲骨文，云业务是未来", "n_likes": 12},
        {"comment_id": "c2", "text": "已经上车了，长期持有", "n_likes": 5},
    ],
)

result, cost, tokens = engine._call_llm(system, user)
print(f"Raw parsed result type: {type(result)}")
print(f"Raw parsed result: {json.dumps(result, ensure_ascii=False, indent=2)}")
print(f"Cost: ${cost}")
print(f"Tokens: {tokens}")
print()

# === 2) Full pipeline test: positive post ===

print("=" * 60)
print("TEST 2: Positive post (no comments)")
print("=" * 60)

post1 = RawPost(
    post_id="test001",
    keyword="甲骨文",
    title="甲骨文财报超预期",
    desc="今日甲骨文发布财报，云业务收入同比增长25%，超出市场预期。股价盘后大涨。",
    text="甲骨文财报超预期\n\n今日甲骨文发布财报，云业务收入同比增长25%，超出市场预期。股价盘后大涨。",
    author_id="user1",
    author_nickname="投资达人",
    image_urls=[],
    n_likes=100,
    n_comments_total=20,
    publish_time_ms=1747104000000,
    publish_date=date(2025, 5, 13),
    comments=[],
    fetched_at=datetime.now(timezone.utc),
)

scored1 = engine.analyze(post1)
print(f"Sentiment: {scored1.sentiment_post}")
print(f"Relevant: {scored1.is_relevant}")
print(f"FOMO: {scored1.fomo}")
print(f"Quote: {scored1.quote}")
print(f"Cost: ${scored1.cost_usd}")
print()

# === 3) Full pipeline test: with comments ===

print("=" * 60)
print("TEST 3: Post with comments")
print("=" * 60)

post2 = post1.model_copy(
    update={
        "post_id": "test002",
        "comments": [
            RawComment(comment_id="c1", text="看好甲骨文，云业务是未来", n_likes=12),
            RawComment(comment_id="c2", text="已经上车了，长期持有", n_likes=5),
        ],
    }
)

scored2 = engine.analyze(post2)
print(f"Sentiment: {scored2.sentiment_post}")
print(f"Relevant: {scored2.is_relevant}")
print(f"FOMO: {scored2.fomo}")
print(f"Quote: {scored2.quote}")
print(f"Comment scores:")
for cs in scored2.comment_scores:
    print(f"  {cs.comment_id}: sentiment={cs.sentiment}, relevant={cs.is_relevant}")
print(f"Comments avg: {scored2.sentiment_comments_avg}")
print(f"Comments std: {scored2.sentiment_comments_std}")
print(f"Cost: ${scored2.cost_usd}")
print()

# === 4) Negative sentiment ===

print("=" * 60)
print("TEST 4: Negative sentiment post")
print("=" * 60)

post3 = post1.model_copy(
    update={
        "post_id": "test003",
        "title": "甲骨文裁员",
        "desc": "甲骨文大规模裁员，员工人心惶惶。股价暴跌。",
        "text": "甲骨文裁员\n\n甲骨文大规模裁员，员工人心惶惶。股价暴跌。",
    }
)

scored3 = engine.analyze(post3)
print(f"Sentiment: {scored3.sentiment_post}")
print(f"Relevant: {scored3.is_relevant}")
print(f"FOMO: {scored3.fomo}")
print(f"Quote: {scored3.quote}")
print(f"Cost: ${scored3.cost_usd}")
print()

# === 5) Irrelevant post ===

print("=" * 60)
print("TEST 5: Irrelevant post (keyword mismatch)")
print("=" * 60)

post4 = post1.model_copy(
    update={
        "post_id": "test004",
        "keyword": "机器人",
        "title": "小孩子的机器人玩具",
        "desc": "给儿子买了一个机器人玩具，他开心得不得了。",
        "text": "小孩子的机器人玩具\n\n给儿子买了一个机器人玩具，他开心得不得了。",
    }
)

scored4 = engine.analyze(post4)
print(f"Sentiment: {scored4.sentiment_post}")
print(f"Relevant: {scored4.is_relevant}")
print(f"Cost: ${scored4.cost_usd}")
print()

# === Summary ===

print("=" * 60)
print(f"SUMMARY: Total cost = ${engine._total_cost_usd:.6f}")
print("=" * 60)
