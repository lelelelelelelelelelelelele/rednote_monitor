"""Prompt template loading and rendering for M2 Sentiment Engine."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

_DEFAULT_PROMPTS_PATH = Path("config/prompts.yaml")


class PromptTemplates:
    """Loads and renders prompt templates from config/prompts.yaml."""

    def __init__(self, path: Path = _DEFAULT_PROMPTS_PATH):
        with path.open("r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f)

    def render_post_sentiment(
        self,
        keyword: str,
        text: str,
        n_likes: int,
        n_comments_total: int,
        author_nickname: str,
        image_urls: list[str],
    ) -> tuple[str, str]:
        """Returns (system_prompt, user_prompt) for post sentiment analysis."""
        system = self._data["post_sentiment"]["system"]

        image_section = ""
        if image_urls:
            image_section = f"This post has {len(image_urls)} image(s) attached (see below)."

        user = self._data["post_sentiment"]["user"].format(
            keyword=keyword,
            text=text,
            image_section=image_section,
            n_likes=n_likes,
            n_comments_total=n_comments_total,
            author_nickname=author_nickname,
        )
        return system, user

    def render_comment_batch(
        self,
        keyword: str,
        post_text: str,
        comments: list[dict],
    ) -> tuple[str, str]:
        """Returns (system_prompt, user_prompt) for batch comment scoring."""
        system = self._data["comment_batch"]["system"]
        user = self._data["comment_batch"]["user"].format(
            keyword=keyword,
            post_text=post_text[:500],
            comments_json=json.dumps(comments, ensure_ascii=False, indent=2),
        )
        return system, user

    def render_per_comment(
        self,
        keyword: str,
        post_text: str,
        comment_text: str,
    ) -> tuple[str, str]:
        """Returns (system_prompt, user_prompt) for single comment scoring (Approach A fallback)."""
        system = self._data["per_comment"]["system"]
        user = self._data["per_comment"]["user"].format(
            keyword=keyword,
            post_text=post_text[:300],
            comment_text=comment_text,
        )
        return system, user
