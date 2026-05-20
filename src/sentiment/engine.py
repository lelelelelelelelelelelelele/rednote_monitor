"""M2 Sentiment Engine — scores a RawPost into a ScoredPost using LLM.

BLUEPRINT § M2:
    单条帖子(含图)+ 评论区 → 结构化情绪打分
    多模态: image 直接喂 vision model,不做 OCR
    polarity 五档: -2 / -1 / 0 / +1 / +2
    帖子主体和评论区分开打分(常常情绪相反)
    LLM 只给 per-comment 离散值,sentiment_comments_avg 客户端按 n_likes 加权得到
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Literal

import litellm

from ..models import CommentScore, RawPost, ScoredPost, SentimentScore
from .prompts import PromptTemplates

logger = logging.getLogger(__name__)

# Suppress litellm's verbose logging
litellm.suppress_debug_info = True


def _strip_markdown_fences(text: str) -> str:
    """Strip ```json ... ``` markdown fences from LLM output."""
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())


def _safe_int(value: Any, valid: set[int], default: int = 0) -> int:
    """Coerce value to int, return default if not in valid set."""
    try:
        v = int(value)
        return v if v in valid else default
    except (TypeError, ValueError):
        return default


class SentimentEngine:
    """Scores a single RawPost into a ScoredPost via LLM.

    Two-phase scoring:
    1. Post body (text + images) -> sentiment_post, is_relevant, fomo, quote
    2. Comments (batch) -> per-comment sentiment + is_relevant

    Client-side post-processing:
    - sentiment_comments_avg = n_likes-weighted average of relevant comment sentiments
    - sentiment_comments_std = standard deviation of relevant comment sentiments
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        prompts_path: str | Path = "config/prompts.yaml",
        mode: Literal["batch", "per_comment"] = "batch",
        max_retries: int = 2,
        fallback_mode: bool = True,
    ):
        self.model = model
        self.mode = mode
        self.max_retries = max_retries
        self.fallback_mode = fallback_mode
        self.prompts = PromptTemplates(Path(prompts_path))
        self._total_cost_usd: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, post: RawPost) -> ScoredPost:
        """Score a single RawPost. This is the BLUEPRINT-specified interface."""
        # Edge case: empty post with no content to score
        if not post.text.strip() and not post.image_urls:
            logger.warning(f"[M2] Post {post.post_id} has no text or images, returning defaults")
            return self._default_scored_post(post)

        # Phase 1: Score post body
        post_result, post_cost = self._score_post(post)

        # Phase 2: Score comments
        comment_scores: list[CommentScore] = []
        comments_cost = 0.0
        if post.comments:
            comment_scores, comments_cost = self._score_comments(post)

        # Phase 3: Client-side aggregation
        n_comments_scored, avg, std = self._aggregate_comments(
            comment_scores, post.comments
        )

        total_cost = post_cost + comments_cost
        self._total_cost_usd += total_cost

        return ScoredPost(
            post_id=post.post_id,
            keyword=post.keyword,
            watchlist_id=post.watchlist_id,
            date=post.publish_date,
            is_relevant=post_result["is_relevant"],
            sentiment_post=post_result["sentiment"],
            comment_scores=comment_scores,
            n_comments_scored=n_comments_scored,
            sentiment_comments_avg=avg,
            sentiment_comments_std=std,
            fomo=post_result.get("fomo", 0),
            quote=post_result.get("quote", ""),
            model=self.model,
            cost_usd=round(total_cost, 6),
        )

    # ------------------------------------------------------------------
    # Phase 1: Post scoring
    # ------------------------------------------------------------------

    def _score_post(self, post: RawPost) -> tuple[dict, float]:
        """Score the post body (text + images). Returns (result_dict, cost_usd)."""
        system, user = self.prompts.render_post_sentiment(
            keyword=post.keyword,
            text=post.text,
            n_likes=post.n_likes,
            n_comments_total=post.n_comments_total,
            author_nickname=post.author_nickname,
            image_urls=post.image_urls,
        )

        last_cost = 0.0
        for attempt in range(self.max_retries + 1):
            try:
                result, cost = self._call_llm(
                    system, user, image_urls=post.image_urls or None
                )
                last_cost = cost
                self._validate_post_result(result)
                result["_cost_usd"] = cost
                return result, cost
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"[M2] Post {post.post_id} attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    logger.error(f"[M2] Post {post.post_id} exhausted retries, using defaults")
                    return {
                        "is_relevant": True,
                        "sentiment": 0,
                        "fomo": 0,
                        "quote": "",
                    }, last_cost

        return {"is_relevant": True, "sentiment": 0, "fomo": 0, "quote": ""}, last_cost

    def _validate_post_result(self, result: dict) -> None:
        """Validate LLM output for post scoring."""
        if not isinstance(result.get("is_relevant"), bool):
            # Coerce string "true"/"false" to bool
            val = result.get("is_relevant")
            if isinstance(val, str):
                result["is_relevant"] = val.lower() in ("true", "1")
            else:
                raise ValueError(f"is_relevant must be bool, got {val}")

        sent = result.get("sentiment")
        if sent not in (-2, -1, 0, 1, 2):
            raise ValueError(f"sentiment must be in [-2,-1,0,1,2], got {sent}")

        fomo = result.get("fomo")
        if fomo is None:
            result["fomo"] = 0
        elif not isinstance(fomo, int) or not (0 <= fomo <= 10):
            # Try to coerce
            try:
                result["fomo"] = max(0, min(10, int(fomo)))
            except (TypeError, ValueError):
                raise ValueError(f"fomo must be int 0-10, got {fomo}")

        if not isinstance(result.get("quote"), str):
            result["quote"] = str(result.get("quote", ""))

    # ------------------------------------------------------------------
    # Phase 2: Comment scoring
    # ------------------------------------------------------------------

    def _score_comments(self, post: RawPost) -> tuple[list[CommentScore], float]:
        """Score all comments. Returns (comment_scores, total_cost_usd)."""
        if self.mode == "batch":
            try:
                return self._score_comments_batch(post)
            except Exception as e:
                if self.fallback_mode:
                    logger.warning(
                        f"[M2] Batch comment scoring failed for post {post.post_id}, "
                        f"falling back to per-comment: {e}"
                    )
                    return self._score_comments_per_comment(post)
                raise
        return self._score_comments_per_comment(post)

    def _score_comments_batch(self, post: RawPost) -> tuple[list[CommentScore], float]:
        """Batch approach: all comments in one LLM call."""
        comments_payload = [
            {"comment_id": c.comment_id, "text": c.text, "n_likes": c.n_likes}
            for c in post.comments
        ]

        system, user = self.prompts.render_comment_batch(
            keyword=post.keyword,
            post_text=post.text,
            comments=comments_payload,
        )

        last_cost = 0.0
        for attempt in range(self.max_retries + 1):
            try:
                result, cost = self._call_llm(system, user)
                last_cost = cost
                scores = self._parse_comment_batch(result, post.comments)
                return scores, cost
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    f"[M2] Comment batch for post {post.post_id} attempt {attempt + 1}: {e}"
                )
                if attempt == self.max_retries:
                    raise

        return [], last_cost

    def _parse_comment_batch(
        self, result: Any, original_comments: list
    ) -> list[CommentScore]:
        """Parse and validate batch comment LLM output."""
        # Handle if LLM wraps in {"comments": [...]}
        if isinstance(result, dict):
            result = result.get("comments", result.get("data", []))

        if not isinstance(result, list):
            raise ValueError(f"Expected list, got {type(result)}")

        original_by_id = {c.comment_id: c for c in original_comments}
        scores: list[CommentScore] = []

        for item in result:
            if not isinstance(item, dict):
                continue
            cid = item.get("comment_id", "")
            if cid not in original_by_id:
                logger.warning(f"[M2] Unknown comment_id {cid} in LLM response, skipping")
                continue
            sent = _safe_int(item.get("sentiment"), {-2, -1, 0, 1, 2}, default=0)
            scores.append(
                CommentScore(
                    comment_id=cid,
                    sentiment=sent,
                    is_relevant=bool(item.get("is_relevant", True)),
                )
            )

        # Fill missing comments with neutral defaults
        scored_ids = {s.comment_id for s in scores}
        for c in original_comments:
            if c.comment_id not in scored_ids:
                logger.warning(f"[M2] Comment {c.comment_id} missing from LLM response, defaulting")
                scores.append(
                    CommentScore(
                        comment_id=c.comment_id,
                        sentiment=0,
                        is_relevant=True,
                    )
                )

        return scores

    def _score_comments_per_comment(
        self, post: RawPost
    ) -> tuple[list[CommentScore], float]:
        """Approach A: one LLM call per comment. Used as fallback or primary."""
        scores: list[CommentScore] = []
        total_cost = 0.0

        for comment in post.comments:
            system, user = self.prompts.render_per_comment(
                keyword=post.keyword,
                post_text=post.text,
                comment_text=comment.text,
            )
            try:
                result, cost = self._call_llm(system, user)
                total_cost += cost
                sent = _safe_int(result.get("sentiment"), {-2, -1, 0, 1, 2}, default=0)
                scores.append(
                    CommentScore(
                        comment_id=comment.comment_id,
                        sentiment=sent,
                        is_relevant=bool(result.get("is_relevant", True)),
                    )
                )
            except Exception as e:
                logger.warning(f"[M2] Failed scoring comment {comment.comment_id}: {e}")
                scores.append(
                    CommentScore(
                        comment_id=comment.comment_id,
                        sentiment=0,
                        is_relevant=True,
                    )
                )

        return scores, total_cost

    # ------------------------------------------------------------------
    # Phase 3: Client-side aggregation
    # ------------------------------------------------------------------

    def _aggregate_comments(
        self,
        comment_scores: list[CommentScore],
        raw_comments: list,
    ) -> tuple[int, float, float]:
        """Compute n_likes-weighted average and std of relevant comment sentiments.

        Returns: (n_comments_scored, avg, std)
        """
        likes_by_id = {c.comment_id: c.n_likes for c in raw_comments}

        relevant = [cs for cs in comment_scores if cs.is_relevant]
        n_scored = len(relevant)

        if n_scored == 0:
            return 0, 0.0, 0.0

        # n_likes-weighted average (min weight = 1)
        total_weight = 0.0
        weighted_sum = 0.0
        values: list[int] = []
        for cs in relevant:
            weight = max(likes_by_id.get(cs.comment_id, 0), 1)
            weighted_sum += cs.sentiment * weight
            total_weight += weight
            values.append(cs.sentiment)

        avg = weighted_sum / total_weight if total_weight > 0 else 0.0

        # Standard deviation (population)
        if n_scored > 1:
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std = variance**0.5
        else:
            std = 0.0

        return n_scored, round(avg, 4), round(std, 4)

    # ------------------------------------------------------------------
    # LLM call
    # ------------------------------------------------------------------

    def _call_llm(
        self,
        system: str,
        user: str,
        image_urls: list[str] | None = None,
    ) -> tuple[Any, float]:
        """Call LLM via litellm. Returns (parsed_json_response, cost_usd).

        For multimodal posts, image_urls are included as image_url content parts.
        """
        messages: list[dict[str, Any]] = [{"role": "system", "content": system}]

        if image_urls:
            content: list[dict[str, Any]] = [{"type": "text", "text": user}]
            for url in image_urls[:4]:  # Cap at 4 images to control cost
                content.append({
                    "type": "image_url",
                    "image_url": {"url": url, "detail": "low"},
                })
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": user})

        response = litellm.completion(
            model=self.model,
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        # Extract cost
        cost = 0.0
        try:
            cost = litellm.completion_cost(
                model=self.model,
                prompt=str(messages),
                completion=response.choices[0].message.content or "",
            )
        except Exception:
            pass  # Cost calculation is best-effort

        raw_text = response.choices[0].message.content or ""

        # Strip markdown fences that some models add
        cleaned = _strip_markdown_fences(raw_text)
        parsed = json.loads(cleaned)

        return parsed, cost

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _default_scored_post(self, post: RawPost) -> ScoredPost:
        """Return a default ScoredPost for posts with no content."""
        return ScoredPost(
            post_id=post.post_id,
            keyword=post.keyword,
            watchlist_id=post.watchlist_id,
            date=post.publish_date,
            is_relevant=True,
            sentiment_post=0,
            comment_scores=[],
            n_comments_scored=0,
            sentiment_comments_avg=0.0,
            sentiment_comments_std=0.0,
            fomo=0,
            quote="",
            model=self.model,
            cost_usd=0.0,
        )


def analyze(
    post: RawPost,
    *,
    model: str = "gpt-4o-mini",
    mode: Literal["batch", "per_comment"] = "batch",
) -> ScoredPost:
    """Module-level convenience function matching BLUEPRINT interface.

    Usage:
        from src.sentiment import analyze
        scored = analyze(raw_post)
    """
    engine = SentimentEngine(model=model, mode=mode)
    return engine.analyze(post)
