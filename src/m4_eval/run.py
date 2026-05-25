"""M4 Eval Bench — 评测 M2 Sentiment Engine 在人工标注集上的准确率。

BLUEPRINT § M4:
    在 200 条人工标注的小红书评论上,横向对比多模型准确率
    分维度统计: easy / medium / hard; sarcasm / novice / normal
    KPI: 整体准确率 >= 75%, 反讽子集 >= 70%, is_relevant F1 >= 0.85
"""

from __future__ import annotations

import csv
import logging
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

from ..m2_sentiment.engine import SentimentEngine
from ..models import (
    EvalReport,
    LabeledSample,
    RawComment,
    RawPost,
)

logger = logging.getLogger(__name__)

# KPI thresholds from BLUEPRINT § 四.B
KPI_ACCURACY = 0.75
KPI_SARCASM_ACCURACY = 0.70
KPI_IS_RELEVANT_F1 = 0.85


def load_labeled_data(
    path: str | Path = "data/eval/labeled_200.csv",
) -> list[LabeledSample]:
    """读取人工标注 CSV,返回 LabeledSample 列表。"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Labeled data not found: {path}")

    samples: list[LabeledSample] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # CSV 布尔值: TRUE/FALSE (大写)
            row["is_relevant_label"] = row["is_relevant_label"].strip().upper() == "TRUE"
            row["n_likes"] = int(row["n_likes"])
            row["sentiment_label"] = int(row["sentiment_label"])
            samples.append(LabeledSample(**row))

    return samples


def _resolve_prompts_path(prompt_id: str) -> Path:
    """解析 prompt_id 到 prompt 文件路径。"""
    if prompt_id == "v1":
        return Path("config/prompts.yaml")
    versioned = Path(f"config/eval_prompts/{prompt_id}.yaml")
    if versioned.exists():
        return versioned
    raise FileNotFoundError(f"Prompt version '{prompt_id}' not found: {versioned}")


def _build_wrapper_post(sample: LabeledSample) -> RawPost:
    """把一条 LabeledSample 包装成 SentimentEngine 能吃的 RawPost。"""
    return RawPost(
        post_id=f"eval_{sample.comment_id}",
        keyword=sample.keyword,
        text=sample.post_text or sample.keyword,
        title="",
        desc=sample.post_text or "",
        author_id="eval",
        author_nickname="eval",
        publish_time_ms=0,
        publish_date=date.today(),
        comments=[
            RawComment(
                comment_id=sample.comment_id,
                text=sample.text,
                n_likes=sample.n_likes,
            )
        ],
        fetched_at=datetime.now(timezone.utc),  # noqa: UP017
    )


def _calc_f1(tp: int, fp: int, fn: int) -> float:
    """计算 F1 score。"""
    if tp + fp == 0 or tp + fn == 0:
        return 0.0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _calc_group_accuracy(
    results: list[tuple[LabeledSample, int, bool]],
    group_key: str,
) -> dict[str, float]:
    """按某个维度分组计算准确率。"""
    groups: dict[str, list[bool]] = defaultdict(list)
    for sample, pred_sent, _ in results:
        key = getattr(sample, group_key)
        groups[key].append(pred_sent == sample.sentiment_label)
    return {k: sum(v) / len(v) for k, v in groups.items()}


def _build_confusion_matrix(
    results: list[tuple[LabeledSample, int, bool]],
) -> dict[str, dict[str, int]]:
    """构建混淆矩阵。"""
    matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for sample, pred_sent, _ in results:
        matrix[str(sample.sentiment_label)][str(pred_sent)] += 1
    return {k: dict(v) for k, v in matrix.items()}


def _generate_markdown_report(report: EvalReport, results_path: Path) -> str:
    """生成 markdown 格式的评测报告。"""
    lines: list[str] = []
    lines.append(f"# M4 Eval Report — {report.model} / {report.prompt_id}")
    lines.append(f"\n**Run date:** {report.run_date}")
    lines.append(f"**Total samples:** {report.total_samples}")
    lines.append(f"**LLM cost:** ${report.total_cost_usd:.4f}")
    lines.append("")

    # KPI summary
    lines.append("## KPI Summary")
    lines.append("")
    acc_ok = report.accuracy >= KPI_ACCURACY
    sarc_ok = report.sarcasm_subset_accuracy >= KPI_SARCASM_ACCURACY
    f1_ok = report.is_relevant_f1 >= KPI_IS_RELEVANT_F1

    lines.append("| KPI | Threshold | Actual | Status |")
    lines.append("|-----|-----------|--------|--------|")
    lines.append(
        f"| Sentiment accuracy | >= {KPI_ACCURACY:.0%} | {report.accuracy:.1%} | "
        f"{'PASS' if acc_ok else 'FAIL'} |"
    )
    lines.append(
        f"| Sarcasm accuracy | >= {KPI_SARCASM_ACCURACY:.0%} | "
        f"{report.sarcasm_subset_accuracy:.1%} | {'PASS' if sarc_ok else 'FAIL'} |"
    )
    lines.append(
        f"| is_relevant F1 | >= {KPI_IS_RELEVANT_F1} | {report.is_relevant_f1:.3f} | "
        f"{'PASS' if f1_ok else 'FAIL'} |"
    )
    lines.append("")

    # Confusion matrix
    lines.append("## Confusion Matrix (sentiment)")
    lines.append("")
    all_labels = sorted(
        set(report.confusion_matrix.keys())
        | {k for v in report.confusion_matrix.values() for k in v}
    )
    header = "Actual \\ Pred | " + " | ".join(all_labels)
    sep = "--- | " + " | ".join(["---"] * len(all_labels))
    lines.append(header)
    lines.append(sep)
    for actual in all_labels:
        row_vals = report.confusion_matrix.get(actual, {})
        cells = [str(row_vals.get(pred, 0)) for pred in all_labels]
        lines.append(f"{actual} | " + " | ".join(cells))
    lines.append("")

    # Accuracy by dimension
    lines.append("## Accuracy by Difficulty")
    lines.append("")
    lines.append("| Difficulty | Accuracy |")
    lines.append("|------------|----------|")
    for diff, acc in sorted(report.accuracy_by_difficulty.items()):
        lines.append(f"| {diff} | {acc:.1%} |")
    lines.append("")

    lines.append("## Accuracy by Style")
    lines.append("")
    lines.append("| Style | Accuracy |")
    lines.append("|-------|----------|")
    for style, acc in sorted(report.accuracy_by_style.items()):
        lines.append(f"| {style} | {acc:.1%} |")
    lines.append("")

    lines.append(f"\n---\n\nResults CSV: `{results_path}`")

    return "\n".join(lines)


def evaluate(
    model: str,
    prompt_id: str = "v1",
    labeled_path: str | Path = "data/eval/labeled_200.csv",
    output_dir: str | Path = "data/eval",
) -> EvalReport:
    """在人工标注集上评测指定模型的 sentiment 打分准确率。

    Args:
        model: LLM 模型名(传给 SentimentEngine)
        prompt_id: prompt 版本号(v1 用默认,其他查 config/eval_prompts/)
        labeled_path: 标注 CSV 路径
        output_dir: 输出目录

    Returns:
        EvalReport 汇总报告
    """
    samples = load_labeled_data(labeled_path)
    if not samples:
        raise ValueError("No labeled samples found")

    prompts_path = _resolve_prompts_path(prompt_id)
    engine = SentimentEngine(
        model=model,
        mode="per_comment",
        prompts_path=prompts_path,
    )

    results: list[tuple[LabeledSample, int, bool]] = []

    for sample in samples:
        wrapper = _build_wrapper_post(sample)
        scored = engine.analyze(wrapper)

        # 提取预测值: wrapper 只有 1 条评论
        if scored.comment_scores:
            cs = scored.comment_scores[0]
            pred_sent = cs.sentiment
            pred_relevant = cs.is_relevant
        else:
            # fallback: engine 没打分,用默认值
            pred_sent = 0
            pred_relevant = True

        results.append((sample, pred_sent, pred_relevant))

    # 计算指标
    total = len(results)
    correct = sum(1 for s, p, _ in results if p == s.sentiment_label)
    accuracy = correct / total

    # is_relevant F1
    tp = sum(1 for s, _, pr in results if pr and s.is_relevant_label)
    fp = sum(1 for s, _, pr in results if pr and not s.is_relevant_label)
    fn = sum(1 for s, _, pr in results if not pr and s.is_relevant_label)
    f1 = _calc_f1(tp, fp, fn)

    # 分维度
    acc_by_diff = _calc_group_accuracy(results, "difficulty")
    acc_by_style = _calc_group_accuracy(results, "style")
    sarcasm_acc = acc_by_style.get("sarcasm", 0.0)

    confusion = _build_confusion_matrix(results)

    today_str = date.today().isoformat()

    report = EvalReport(
        model=model,
        prompt_id=prompt_id,
        total_samples=total,
        accuracy=round(accuracy, 4),
        accuracy_by_difficulty=acc_by_diff,
        accuracy_by_style=acc_by_style,
        sarcasm_subset_accuracy=round(sarcasm_acc, 4),
        is_relevant_f1=round(f1, 4),
        confusion_matrix=confusion,
        total_cost_usd=round(engine._total_cost_usd, 6),
        run_date=today_str,
    )

    # 写结果 CSV
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / f"results_{today_str}.csv"

    with results_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "comment_id", "keyword", "difficulty", "style",
            "sentiment_label", "sentiment_predicted",
            "is_relevant_label", "is_relevant_predicted", "correct",
        ])
        for sample, pred_sent, pred_rel in results:
            writer.writerow([
                sample.comment_id, sample.keyword,
                sample.difficulty, sample.style,
                sample.sentiment_label, pred_sent,
                sample.is_relevant_label, pred_rel,
                pred_sent == sample.sentiment_label,
            ])

    # 写 markdown 报告
    md_path = output_dir / f"results_{today_str}.md"
    md_content = _generate_markdown_report(report, results_path)
    md_path.write_text(md_content, encoding="utf-8")

    logger.info(
        f"[M4] Eval complete: accuracy={accuracy:.1%}, sarcasm={sarcasm_acc:.1%}, F1={f1:.3f}"
    )
    logger.info(f"[M4] Results: {results_path}")
    logger.info(f"[M4] Report: {md_path}")

    return report
