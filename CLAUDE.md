# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`rednote-monitor` is a Xiaohongshu (Little Red Book) stock sentiment monitoring system. It scrapes retail investor discussions, scores them with multimodal LLMs, and aggregates daily metrics for contrarian trading signals. Python 3.11+, using `uv` as package manager.

## Commands

| Action | Command |
|---|---|
| Install deps | `uv sync` |
| Run all tests | `uv run pytest` |
| Run single test | `uv run pytest tests/scraper/test_xhs_mcp.py` |
| Lint | `uv run ruff check .` |
| Lint + auto-fix | `uv run ruff check --fix .` |
| Type check | `uv run mypy src/` |
| Daily pipeline | `uv run python scripts/daily_run.py --date YYYY-MM-DD` |

## Architecture

7-module pipeline communicating via JSONL files and SQLite. Full design in `BLUEPRINT.md`.

```
M1 Scraper → RawPost (JSONL) → M2 Sentiment → ScoredPost (JSONL) → M3 Aggregator → SQLite
```

Planned: M4 Eval Bench, M5 Backtest, M6 Dashboard (Streamlit), M7 Notify.

**Key files:**
- `src/models.py` — Central data contracts (Pydantic v2). All modules depend on it. **Changes require coordination.**
- `src/scraper/base.py` — `Scraper` Protocol. All scrapers implement `async fetch(keyword, date) -> list[RawPost]`.
- `src/scraper/fallback.py` — FallbackScraper: XhsMcpScraper → ManualScraper auto-degradation.
- `src/sentiment/engine.py` — Two-phase LLM scoring (post body multimodal, then comments via LiteLLM).
- `src/sentiment/prompts.py` — Loads prompt templates from `config/prompts.yaml`.
- `config/watchlist.yaml` — Ticker definitions and keywords.
- `config/prompts.yaml` — LLM prompt templates for post/comment scoring.
- `scripts/daily_run.py` — Daily pipeline orchestrator (M1→M2→M3).

## Tech Stack

- **Validation:** Pydantic v2 | **Storage:** SQLModel + SQLite | **LLM:** LiteLLM (multi-model)
- **Scraping:** xiaohongshu-mcp (third-party, in `external/`, gitignored)
- **Linting:** Ruff (E/F/I/UP/B rules, line-length=100) | **Types:** mypy (strict mode)
- **Testing:** pytest + pytest-asyncio

## Important Conventions

- **`src/models.py` is the most conflict-prone file** — all modules depend on it. Coordinate before modifying.
- **`data/raw/` contains real user data** (nicknames, IP addresses) — never commit. Share sanitized samples in `tests/fixtures/`.
- **`external/` is gitignored** — xiaohongshu-mcp must be installed separately per its upstream README.
- **`post_id` encodes publish time:** `int(post_id[:8], 16)` gives Unix seconds. Used for client-side date filtering.
- **Keyword ambiguity is expected:** "甲骨文" matches calligraphy, "机器人" matches crafts. M2 outputs `is_relevant`; M3 filters on it.
- **Comment scoring:** LLM gives discrete per-comment scores only. The continuous `sentiment_comments_avg` is computed client-side with `n_likes` weighting.
