"""M4 半自动标注工具。

用法:
    # Step 1: LLM 自动预标注
    python scripts/label_helper.py --auto-label

    # Step 2: 人工校验
    python scripts/label_helper.py --review
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import httpx

from src.models import parse_xhs_feed_detail


def _load_comments_from_raw(input_dir: Path) -> list[dict]:
    """从 data/raw/manual/*.json 提取所有评论(去重)。"""
    seen_ids: set[str] = set()
    comments: list[dict] = []

    for json_path in sorted(input_dir.glob("*.json")):
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        # 从文件名或 _meta 提取 keyword
        meta = payload.get("_meta", {})
        keyword = meta.get("keyword", json_path.stem.split("_")[1] if "_" in json_path.stem else "")

        try:
            post = parse_xhs_feed_detail(payload, keyword=keyword)
        except Exception:
            continue

        for c in post.comments:
            if c.comment_id in seen_ids:
                continue
            seen_ids.add(c.comment_id)
            comments.append({
                "comment_id": c.comment_id,
                "keyword": keyword,
                "text": c.text,
                "n_likes": c.n_likes,
                "post_text": post.text,
            })

    return comments


def _call_llm_for_label(
    system: str,
    user: str,
    base_url: str,
    api_key: str,
    model: str,
) -> dict:
    """调用 LLM 做自动标注。"""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    with httpx.Client(timeout=120) as client:
        resp = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()

    data = resp.json()
    raw = data["choices"][0]["message"]["content"] or "{}"
    # strip markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(raw)


def auto_label(
    input_dir: Path,
    output_path: Path,
    prompts_path: Path,
    base_url: str,
    api_key: str,
    model: str,
) -> None:
    """LLM 自动预标注所有评论。"""
    import yaml

    prompts = yaml.safe_load(prompts_path.read_text(encoding="utf-8"))
    label_prompt = prompts.get("eval_label", {})
    system = label_prompt.get("system", "")
    user_tpl = label_prompt.get("user", "")

    comments = _load_comments_from_raw(input_dir)
    if not comments:
        print(f"No comments found in {input_dir}")
        return

    print(f"Found {len(comments)} unique comments. Auto-labeling...")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sarcasm_count = 0

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "comment_id", "keyword", "text", "n_likes", "post_text",
            "difficulty", "style", "sentiment_label", "is_relevant_label",
        ])

        for i, c in enumerate(comments):
            user_msg = user_tpl.format(
                keyword=c["keyword"],
                post_text=c["post_text"][:500],
                comment_text=c["text"],
            )
            try:
                result = _call_llm_for_label(system, user_msg, base_url, api_key, model)
            except Exception as e:
                print(f"  [{i+1}/{len(comments)}] Error for {c['comment_id']}: {e}")
                result = {
                    "sentiment": 0, "is_relevant": True,
                    "difficulty": "medium", "style": "normal",
                }

            sentiment = result.get("sentiment", 0)
            is_relevant = result.get("is_relevant", True)
            difficulty = result.get("difficulty", "medium")
            style = result.get("style", "normal")

            if style == "sarcasm":
                sarcasm_count += 1

            writer.writerow([
                c["comment_id"], c["keyword"], c["text"], c["n_likes"],
                c["post_text"], difficulty, style, sentiment,
                "TRUE" if is_relevant else "FALSE",
            ])

            if (i + 1) % 10 == 0:
                print(f"  [{i+1}/{len(comments)}] done")

    print(f"\nWrote {len(comments)} samples to {output_path}")
    if sarcasm_count < 30:
        print(f"WARNING: Only {sarcasm_count} sarcasm-labeled comments (need >= 30)."
              " Please manually add more sarcastic comments.")


def review(input_path: Path, output_path: Path) -> None:
    """人工校验自动标注结果。"""
    rows: list[dict] = []
    with input_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print("No data to review.")
        return

    print(f"Reviewing {len(rows)} samples from {input_path}")
    print("Commands: Enter=accept, 'q'=save & quit, 's N'=skip to N")
    print("-" * 60)

    i = 0
    while i < len(rows):
        row = rows[i]
        print(f"\n[{i+1}/{len(rows)}] ID={row['comment_id']}  keyword={row['keyword']}")
        print(f"  Text: {row['text']}")
        print(f"  Post: {row['post_text'][:100]}...")
        print(f"  Current: sentiment={row['sentiment_label']}  relevant={row['is_relevant_label']}"
              f"  difficulty={row['difficulty']}  style={row['style']}")

        cmd = input("  > ").strip()

        if cmd == "q":
            break
        elif cmd.startswith("s "):
            try:
                i = int(cmd.split()[1]) - 1
            except ValueError:
                print("  Invalid jump target")
            continue
        elif cmd == "":
            i += 1
            continue
        else:
            # Parse: "sentiment=X relevant=Y difficulty=Z style=W"
            parts = cmd.split()
            for part in parts:
                if "=" in part:
                    k, v = part.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if k == "sentiment":
                        row["sentiment_label"] = v
                    elif k == "relevant":
                        row["is_relevant_label"] = v.upper()
                    elif k == "difficulty":
                        row["difficulty"] = v
                    elif k == "style":
                        row["style"] = v
            i += 1

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "comment_id", "keyword", "text", "n_likes", "post_text",
            "difficulty", "style", "sentiment_label", "is_relevant_label",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} reviewed samples to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="M4 semi-automatic labeling tool")
    parser.add_argument("--auto-label", action="store_true", help="Run LLM auto-labeling")
    parser.add_argument("--review", action="store_true", help="Review and correct auto-labels")
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/manual"),
                        help="Directory with raw JSON files (for --auto-label)")
    parser.add_argument("--input", type=Path, default=Path("data/eval/labeled_auto.csv"),
                        help="Input CSV for --review")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output CSV path (auto-detected by mode)")
    parser.add_argument("--prompts", type=Path, default=Path("config/prompts.yaml"),
                        help="Prompts YAML file")
    parser.add_argument("--model", type=str, default=None,
                        help="LLM model name (default from env)")
    parser.add_argument("--base-url", type=str, default=None,
                        help="LLM base URL (default from env)")
    parser.add_argument("--api-key", type=str, default=None,
                        help="LLM API key (default from env)")

    args = parser.parse_args()

    if not args.auto_label and not args.review:
        parser.error("Must specify --auto-label or --review")

    import os
    base_url = args.base_url or os.environ.get("LLM_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")
    api_key = args.api_key or os.environ.get("LLM_API_KEY", "")
    model = args.model or os.environ.get("LLM_MODEL", "mimo-v2.5-pro")

    if args.auto_label:
        output = args.output or Path("data/eval/labeled_auto.csv")
        auto_label(args.input_dir, output, args.prompts, base_url, api_key, model)

    if args.review:
        output = args.output or Path("data/eval/labeled_200.csv")
        review(args.input, output)


if __name__ == "__main__":
    main()
