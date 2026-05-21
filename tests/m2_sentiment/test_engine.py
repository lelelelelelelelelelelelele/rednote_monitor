"""M2 Sentiment Engine 单元测试。

所有测试 mock LLM 调用,不依赖真实 API key。
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.models import CommentScore, RawComment, RawPost
from src.m2_sentiment.engine import SentimentEngine, _strip_markdown_fences, analyze
from src.m2_sentiment.prompts import PromptTemplates


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #


@pytest.fixture
def sample_post():
    """Minimal RawPost matching the oracle test data structure."""
    return RawPost(
        post_id="6823a1b400000000010001",
        keyword="甲骨文",
        watchlist_id="oracle",
        title="甲骨文 ORCL 财报超预期",
        desc="今日甲骨文发布财报，云业务收入同比增长 25%，超出市场预期。股价盘后大涨。",
        text="甲骨文 ORCL 财报超预期\n\n今日甲骨文发布财报，云业务收入同比增长 25%，超出市场预期。股价盘后大涨。",
        author_id="user001",
        author_nickname="投资达人",
        image_urls=[],
        n_likes=234,
        n_comments_total=87,
        publish_time_ms=1747104000000,
        publish_date=date(2025, 5, 13),
        comments=[
            RawComment(comment_id="c1", text="看好甲骨文，云业务是未来", n_likes=12),
            RawComment(comment_id="c2", text="已经上车了，长期持有", n_likes=5),
        ],
        fetched_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def empty_comments_post(sample_post):
    """Post with no comments."""
    return sample_post.model_copy(update={"comments": []})


@pytest.fixture
def post_with_images(sample_post):
    """Post with image URLs."""
    return sample_post.model_copy(
        update={"image_urls": ["https://example.com/chart.jpg", "https://example.com/meme.jpg"]}
    )


@pytest.fixture
def mock_post_response():
    return {
        "is_relevant": True,
        "sentiment": 2,
        "fomo": 7,
        "quote": "云业务收入同比增长 25%，超出市场预期",
    }


@pytest.fixture
def mock_comment_batch_response():
    return [
        {"comment_id": "c1", "sentiment": 2, "is_relevant": True},
        {"comment_id": "c2", "sentiment": 1, "is_relevant": True},
    ]


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #


def _mock_llm(return_value, cost=0.001, tokens=100):
    """Create a mock _call_llm that returns (parsed_json, cost, tokens)."""
    def _side_effect(system, user, image_urls=None):
        return return_value, cost, tokens
    return _side_effect


def _mock_llm_sequence(responses):
    """Create a mock _call_llm that returns different values on successive calls."""
    iter_responses = iter(responses)
    def _side_effect(system, user, image_urls=None):
        val, cost, tokens = next(iter_responses)
        return val, cost, tokens
    return _side_effect


# ------------------------------------------------------------------ #
# Tests: Utility functions
# ------------------------------------------------------------------ #


class TestStripMarkdownFences:
    def test_strips_json_fence(self):
        assert _strip_markdown_fences('```json\n{"key": "value"}\n```') == '{"key": "value"}'

    def test_strips_plain_fence(self):
        assert _strip_markdown_fences('```\n{"key": "value"}\n```') == '{"key": "value"}'

    def test_no_fence(self):
        assert _strip_markdown_fences('{"key": "value"}') == '{"key": "value"}'

    def test_strips_whitespace(self):
        assert _strip_markdown_fences('  \n{"key": "value"}\n  ') == '{"key": "value"}'


# ------------------------------------------------------------------ #
# Tests: Prompt rendering
# ------------------------------------------------------------------ #


class TestPromptTemplates:
    def test_render_post_sentiment(self):
        templates = PromptTemplates(Path("config/prompts.yaml"))
        system, user = templates.render_post_sentiment(
            keyword="甲骨文",
            text="测试文本",
            n_likes=100,
            n_comments_total=20,
            author_nickname="测试用户",
            image_urls=[],
        )
        assert "甲骨文" in user
        assert "测试文本" in user
        assert "100" in user
        assert "测试用户" in user
        assert "image" not in user.lower() or "no image" in user.lower() or "attached" not in user.lower()

    def test_render_post_with_images(self):
        templates = PromptTemplates(Path("config/prompts.yaml"))
        _, user = templates.render_post_sentiment(
            keyword="test",
            text="text",
            n_likes=0,
            n_comments_total=0,
            author_nickname="",
            image_urls=["http://example.com/1.jpg", "http://example.com/2.jpg"],
        )
        assert "2 image(s)" in user

    def test_render_comment_batch(self):
        templates = PromptTemplates(Path("config/prompts.yaml"))
        comments = [
            {"comment_id": "c1", "text": "看好", "n_likes": 10},
            {"comment_id": "c2", "text": "看空", "n_likes": 5},
        ]
        system, user = templates.render_comment_batch(
            keyword="甲骨文",
            post_text="帖子内容",
            comments=comments,
        )
        assert "甲骨文" in user
        assert "c1" in user
        assert "看好" in user

    def test_render_per_comment(self):
        templates = PromptTemplates(Path("config/prompts.yaml"))
        system, user = templates.render_per_comment(
            keyword="甲骨文",
            post_text="帖子内容",
            comment_text="评论内容",
        )
        assert "评论内容" in user


# ------------------------------------------------------------------ #
# Tests: Post scoring
# ------------------------------------------------------------------ #


class TestScorePost:
    def test_happy_path(self, sample_post, mock_post_response):
        engine = SentimentEngine(model="test-model")
        with patch.object(engine, "_call_llm", side_effect=_mock_llm(mock_post_response)):
            result, cost, tokens = engine._score_post(sample_post)

        assert result["is_relevant"] is True
        assert result["sentiment"] == 2
        assert result["fomo"] == 7
        assert "云业务" in result["quote"]
        assert cost > 0

    def test_irrelevant_post(self, sample_post):
        engine = SentimentEngine(model="test-model")
        response = {
            "is_relevant": False,
            "sentiment": 0,
            "fomo": 0,
            "quote": "甲骨文是古代文字",
        }
        with patch.object(engine, "_call_llm", side_effect=_mock_llm(response)):
            result, _, _ = engine._score_post(sample_post)

        assert result["is_relevant"] is False

    def test_is_relevant_string_coercion(self, sample_post):
        """LLM returns 'true' as string instead of bool."""
        engine = SentimentEngine(model="test-model")
        response = {"is_relevant": "true", "sentiment": 1, "fomo": 3, "quote": "test"}
        with patch.object(engine, "_call_llm", side_effect=_mock_llm(response)):
            result, _, _ = engine._score_post(sample_post)

        assert result["is_relevant"] is True

    def test_invalid_sentiment_retries_then_defaults(self, sample_post):
        """Invalid sentiment retries then returns safe defaults."""
        engine = SentimentEngine(model="test-model", max_retries=0)
        response = {"is_relevant": True, "sentiment": 3, "fomo": 5, "quote": "test"}
        with patch.object(engine, "_call_llm", side_effect=_mock_llm(response)):
            result, _, _ = engine._score_post(sample_post)

        assert result["sentiment"] == 0  # default after exhausted retries

    def test_fomo_clamping(self, sample_post):
        """LLM returns fomo=15, should be clamped to 10."""
        engine = SentimentEngine(model="test-model")
        response = {"is_relevant": True, "sentiment": 0, "fomo": 15, "quote": "test"}
        with patch.object(engine, "_call_llm", side_effect=_mock_llm(response)):
            result, _, _ = engine._score_post(sample_post)

        assert result["fomo"] == 10

    def test_retry_on_malformed_json(self, sample_post, mock_post_response):
        """First call fails, second succeeds."""
        engine = SentimentEngine(model="test-model", max_retries=2)
        call_count = 0

        def _flaky_llm(system, user, image_urls=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise json.JSONDecodeError("bad", "", 0)
            return mock_post_response, 0.001, 100

        with patch.object(engine, "_call_llm", side_effect=_flaky_llm):
            result, _, _ = engine._score_post(sample_post)

        assert result["sentiment"] == 2
        assert call_count == 2

    def test_exhausted_retries_returns_defaults(self, sample_post):
        engine = SentimentEngine(model="test-model", max_retries=0)
        with patch.object(
            engine, "_call_llm", side_effect=json.JSONDecodeError("bad", "", 0)
        ):
            result, cost, tokens = engine._score_post(sample_post)

        assert result["is_relevant"] is True
        assert result["sentiment"] == 0


# ------------------------------------------------------------------ #
# Tests: Comment scoring
# ------------------------------------------------------------------ #


class TestScoreComments:
    def test_batch_happy_path(self, sample_post, mock_comment_batch_response):
        engine = SentimentEngine(model="test-model", mode="batch")
        with patch.object(
            engine, "_call_llm", side_effect=_mock_llm(mock_comment_batch_response)
        ):
            scores, cost, tokens = engine._score_comments_batch(sample_post)

        assert len(scores) == 2
        assert scores[0].comment_id == "c1"
        assert scores[0].sentiment == 2
        assert scores[1].comment_id == "c2"
        assert scores[1].sentiment == 1

    def test_batch_wrapped_in_dict(self, sample_post):
        """LLM wraps response in {"comments": [...]}."""
        engine = SentimentEngine(model="test-model", mode="batch")
        wrapped = {
            "comments": [
                {"comment_id": "c1", "sentiment": 1, "is_relevant": True},
                {"comment_id": "c2", "sentiment": -1, "is_relevant": True},
            ]
        }
        with patch.object(engine, "_call_llm", side_effect=_mock_llm(wrapped)):
            scores, _, _ = engine._score_comments_batch(sample_post)

        assert len(scores) == 2
        assert scores[0].sentiment == 1

    def test_batch_missing_comment_fills_default(self, sample_post):
        """LLM only returns 1 of 2 comments — missing one gets default."""
        engine = SentimentEngine(model="test-model", mode="batch")
        partial = [{"comment_id": "c1", "sentiment": 2, "is_relevant": True}]
        with patch.object(engine, "_call_llm", side_effect=_mock_llm(partial)):
            scores, _, _ = engine._score_comments_batch(sample_post)

        assert len(scores) == 2
        c2_score = next(s for s in scores if s.comment_id == "c2")
        assert c2_score.sentiment == 0
        assert c2_score.is_relevant is True

    def test_batch_invalid_sentiment_defaults_to_zero(self, sample_post):
        engine = SentimentEngine(model="test-model", mode="batch")
        response = [
            {"comment_id": "c1", "sentiment": 99, "is_relevant": True},
            {"comment_id": "c2", "sentiment": -2, "is_relevant": False},
        ]
        with patch.object(engine, "_call_llm", side_effect=_mock_llm(response)):
            scores, _, _ = engine._score_comments_batch(sample_post)

        c1_score = next(s for s in scores if s.comment_id == "c1")
        assert c1_score.sentiment == 0  # invalid -> default

    def test_batch_fallback_to_per_comment(self, sample_post):
        """Batch fails, fallback to per_comment mode."""
        engine = SentimentEngine(model="test-model", mode="batch", fallback_mode=True)

        with patch.object(engine, "_score_comments_batch", side_effect=ValueError("batch failed")):
            with patch.object(engine, "_score_comments_per_comment", return_value=(
                [
                    CommentScore(comment_id="c1", sentiment=2, is_relevant=True),
                    CommentScore(comment_id="c2", sentiment=-1, is_relevant=True),
                ],
                0.002,
                200,
            )):
                scores, cost, tokens = engine._score_comments(sample_post)

        assert len(scores) == 2

    def test_per_comment_happy_path(self, sample_post):
        engine = SentimentEngine(model="test-model", mode="per_comment")
        responses = [
            ({"sentiment": 2, "is_relevant": True}, 0.001, 100),
            ({"sentiment": -1, "is_relevant": True}, 0.001, 100),
        ]
        with patch.object(engine, "_call_llm", side_effect=_mock_llm_sequence(responses)):
            scores, cost, tokens = engine._score_comments_per_comment(sample_post)

        assert len(scores) == 2
        assert scores[0].sentiment == 2
        assert scores[1].sentiment == -1

    def test_per_comment_failure_uses_default(self, sample_post):
        engine = SentimentEngine(model="test-model", mode="per_comment")
        call_count = 0

        def _flaky(system, user, image_urls=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("API error")
            return {"sentiment": 1, "is_relevant": True}, 0.001, 100

        with patch.object(engine, "_call_llm", side_effect=_flaky):
            scores, _, _ = engine._score_comments_per_comment(sample_post)

        assert len(scores) == 2
        assert scores[0].sentiment == 0  # default on failure
        assert scores[1].sentiment == 1  # success


# ------------------------------------------------------------------ #
# Tests: Aggregation
# ------------------------------------------------------------------ #


class TestAggregateComments:
    def test_weighted_average(self):
        engine = SentimentEngine()
        comment_scores = [
            CommentScore(comment_id="c1", sentiment=2, is_relevant=True),   # n_likes=12
            CommentScore(comment_id="c2", sentiment=-1, is_relevant=True),  # n_likes=5
        ]
        raw_comments = [
            RawComment(comment_id="c1", text="", n_likes=12),
            RawComment(comment_id="c2", text="", n_likes=5),
        ]

        n, avg, std = engine._aggregate_comments(comment_scores, raw_comments)

        # weighted_avg = (2*12 + (-1)*5) / (12+5) = 19/17 ≈ 1.1176
        assert n == 2
        assert abs(avg - 1.1176) < 0.01
        assert std > 0

    def test_all_irrelevant(self):
        engine = SentimentEngine()
        comment_scores = [
            CommentScore(comment_id="c1", sentiment=2, is_relevant=False),
            CommentScore(comment_id="c2", sentiment=-1, is_relevant=False),
        ]
        raw_comments = [
            RawComment(comment_id="c1", text="", n_likes=12),
            RawComment(comment_id="c2", text="", n_likes=5),
        ]

        n, avg, std = engine._aggregate_comments(comment_scores, raw_comments)

        assert n == 0
        assert avg == 0.0
        assert std == 0.0

    def test_single_comment_std_zero(self):
        engine = SentimentEngine()
        comment_scores = [
            CommentScore(comment_id="c1", sentiment=1, is_relevant=True),
        ]
        raw_comments = [
            RawComment(comment_id="c1", text="", n_likes=10),
        ]

        n, avg, std = engine._aggregate_comments(comment_scores, raw_comments)

        assert n == 1
        assert avg == 1.0
        assert std == 0.0

    def test_zero_likes_min_weight(self):
        """Comments with 0 likes should still have weight=1."""
        engine = SentimentEngine()
        comment_scores = [
            CommentScore(comment_id="c1", sentiment=2, is_relevant=True),
            CommentScore(comment_id="c2", sentiment=-2, is_relevant=True),
        ]
        raw_comments = [
            RawComment(comment_id="c1", text="", n_likes=0),
            RawComment(comment_id="c2", text="", n_likes=0),
        ]

        n, avg, std = engine._aggregate_comments(comment_scores, raw_comments)

        # Both weight=1, so avg = (2 + -2) / 2 = 0
        assert n == 2
        assert avg == 0.0

    def test_empty_scores(self):
        engine = SentimentEngine()
        n, avg, std = engine._aggregate_comments([], [])
        assert n == 0
        assert avg == 0.0
        assert std == 0.0


# ------------------------------------------------------------------ #
# Tests: Full analyze() pipeline
# ------------------------------------------------------------------ #


class TestAnalyze:
    def test_full_pipeline(
        self, sample_post, mock_post_response, mock_comment_batch_response
    ):
        engine = SentimentEngine(model="test-model")
        with patch.object(
            engine,
            "_call_llm",
            side_effect=_mock_llm_sequence([
                (mock_post_response, 0.001, 100),
                (mock_comment_batch_response, 0.001, 100),
            ]),
        ):
            scored = engine.analyze(sample_post)

        assert scored.post_id == "6823a1b400000000010001"
        assert scored.keyword == "甲骨文"
        assert scored.watchlist_id == "oracle"
        assert scored.date == date(2025, 5, 13)
        assert scored.sentiment_post == 2
        assert scored.is_relevant is True
        assert scored.fomo == 7
        assert "云业务" in scored.quote
        assert len(scored.comment_scores) == 2
        assert scored.n_comments_scored == 2
        assert scored.model == "test-model"
        assert scored.cost_usd > 0

    def test_no_comments(self, empty_comments_post, mock_post_response):
        engine = SentimentEngine(model="test-model")
        with patch.object(engine, "_call_llm", side_effect=_mock_llm(mock_post_response)):
            scored = engine.analyze(empty_comments_post)

        assert scored.comment_scores == []
        assert scored.n_comments_scored == 0
        assert scored.sentiment_comments_avg == 0.0
        assert scored.sentiment_comments_std == 0.0

    def test_with_images(self, post_with_images, mock_post_response, mock_comment_batch_response):
        engine = SentimentEngine(model="test-model")
        captured_args = []

        def _capture_llm(system, user, image_urls=None):
            captured_args.append({"image_urls": image_urls})
            if len(captured_args) == 1:
                return mock_post_response, 0.001, 100
            return mock_comment_batch_response, 0.001, 100

        with patch.object(engine, "_call_llm", side_effect=_capture_llm):
            scored = engine.analyze(post_with_images)

        # Post scoring should have received image_urls
        assert captured_args[0]["image_urls"] is not None
        assert len(captured_args[0]["image_urls"]) == 2

    def test_empty_post_returns_defaults(self, sample_post):
        """Post with empty text and no images returns defaults without LLM call."""
        empty_post = sample_post.model_copy(update={"text": "", "image_urls": []})
        engine = SentimentEngine(model="test-model")
        with patch.object(engine, "_call_llm") as mock_llm:
            scored = engine.analyze(empty_post)

        mock_llm.assert_not_called()
        assert scored.sentiment_post == 0
        assert scored.is_relevant is True
        assert scored.cost_usd == 0.0

    def test_module_level_analyze(self, sample_post, mock_post_response, mock_comment_batch_response):
        """Test the module-level analyze() convenience function."""
        with patch.object(SentimentEngine, "_call_llm") as mock_llm:
            mock_llm.side_effect = _mock_llm_sequence([
                (mock_post_response, 0.001, 100),
                (mock_comment_batch_response, 0.001, 100),
            ])
            scored = analyze(sample_post, model="test-model")

        assert scored.sentiment_post == 2
        assert scored.model == "test-model"


# ------------------------------------------------------------------ #
# Tests: Cost tracking
# ------------------------------------------------------------------ #


class TestCostTracking:
    def test_cost_accumulated(self, sample_post, mock_post_response, mock_comment_batch_response):
        engine = SentimentEngine(model="test-model")
        with patch.object(
            engine,
            "_call_llm",
            side_effect=_mock_llm_sequence([
                (mock_post_response, 0.003, 300),
                (mock_comment_batch_response, 0.002, 200),
            ]),
        ):
            scored = engine.analyze(sample_post)

        assert scored.cost_usd == pytest.approx(0.005, abs=0.0001)
        assert engine._total_cost_usd == pytest.approx(0.005, abs=0.0001)

    def test_cost_tracking_across_posts(self, sample_post, mock_post_response):
        engine = SentimentEngine(model="test-model")
        call_count = 0
        def _cost_llm(system, user, image_urls=None):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 1:  # odd calls = post scoring
                return dict(mock_post_response), 0.003, 300
            return [{"comment_id": "c1", "sentiment": 1, "is_relevant": True},
                     {"comment_id": "c2", "sentiment": 1, "is_relevant": True}], 0.001, 100

        with patch.object(engine, "_call_llm", side_effect=_cost_llm):
            engine.analyze(sample_post)
            engine.analyze(sample_post)

        assert engine._total_cost_usd == pytest.approx(0.008, abs=0.0001)

    def test_token_tracking(self, sample_post, mock_post_response, mock_comment_batch_response):
        engine = SentimentEngine(model="test-model")
        with patch.object(
            engine,
            "_call_llm",
            side_effect=_mock_llm_sequence([
                (mock_post_response, 0.001, 150),
                (mock_comment_batch_response, 0.001, 200),
            ]),
        ):
            engine.analyze(sample_post)

        assert engine._total_tokens == 350


# ------------------------------------------------------------------ #
# Tests: Config via env vars
# ------------------------------------------------------------------ #


class TestEnvVarConfig:
    def test_model_from_env(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL", "custom-model")
        engine = SentimentEngine()
        assert engine.model == "custom-model"

    def test_base_url_from_env(self, monkeypatch):
        monkeypatch.setenv("LLM_BASE_URL", "https://custom.api.com/v1")
        engine = SentimentEngine()
        assert engine.base_url == "https://custom.api.com/v1"

    def test_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("LLM_API_KEY", "sk-test-123")
        engine = SentimentEngine()
        assert engine.api_key == "sk-test-123"

    def test_constructor_overrides_env(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL", "env-model")
        engine = SentimentEngine(model="constructor-model")
        assert engine.model == "constructor-model"

    def test_default_model(self):
        engine = SentimentEngine()
        assert engine.model == "mimo-v2.5-pro"

    def test_default_base_url(self):
        engine = SentimentEngine()
        assert engine.base_url == "https://token-plan-cn.xiaomimimo.com/v1"
