"""M4 Eval Bench 单元测试。

所有测试 mock LLM 调用,不依赖真实 API key。
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from src.m2_sentiment.engine import SentimentEngine
from src.m4_eval.run import (
    _calc_f1,
    _calc_group_accuracy,
    _generate_markdown_report,
    _resolve_prompts_path,
    evaluate,
    load_labeled_data,
)
from src.models import (
    CommentScore,
    EvalReport,
    LabeledSample,
    ScoredPost,
)

# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #


@pytest.fixture
def sample_labeled_data():
    """5 条标注样本,覆盖不同维度。"""
    return [
        LabeledSample(
            comment_id="c1", keyword="甲骨文", text="看好", n_likes=10,
            post_text="甲骨文财报超预期", difficulty="easy", style="normal",
            sentiment_label=2, is_relevant_label=True,
        ),
        LabeledSample(
            comment_id="c2", keyword="甲骨文", text="韭菜本菜", n_likes=5,
            post_text="甲骨文财报超预期", difficulty="hard", style="sarcasm",
            sentiment_label=-1, is_relevant_label=True,
        ),
        LabeledSample(
            comment_id="c3", keyword="甲骨文", text="今天天气不错", n_likes=0,
            post_text="甲骨文财报超预期", difficulty="easy", style="normal",
            sentiment_label=0, is_relevant_label=False,
        ),
        LabeledSample(
            comment_id="c4", keyword="机器人", text="这个玩具好可爱", n_likes=3,
            post_text="机器人ETF讨论", difficulty="medium", style="novice",
            sentiment_label=0, is_relevant_label=False,
        ),
        LabeledSample(
            comment_id="c5", keyword="甲骨文", text="垃圾股", n_likes=8,
            post_text="甲骨文财报超预期", difficulty="medium", style="normal",
            sentiment_label=-2, is_relevant_label=True,
        ),
    ]


def _write_csv(path: Path, samples: list[LabeledSample]) -> None:
    """把 LabeledSample 列表写成 CSV。"""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "comment_id", "keyword", "text", "n_likes", "post_text",
            "difficulty", "style", "sentiment_label", "is_relevant_label",
        ])
        for s in samples:
            writer.writerow([
                s.comment_id, s.keyword, s.text, s.n_likes, s.post_text,
                s.difficulty, s.style, s.sentiment_label,
                "TRUE" if s.is_relevant_label else "FALSE",
            ])


def _mock_llm(return_value, cost=0.001, tokens=100):
    def _side_effect(system, user, image_urls=None):
        return return_value, cost, tokens
    return _side_effect


def _mock_llm_sequence(responses):
    iter_responses = iter(responses)
    def _side_effect(system, user, image_urls=None):
        val, cost, tokens = next(iter_responses)
        return val, cost, tokens
    return _side_effect


# ------------------------------------------------------------------ #
# Tests: load_labeled_data
# ------------------------------------------------------------------ #


class TestLoadLabeledData:
    def test_loads_valid_csv(self, tmp_path, sample_labeled_data):
        csv_path = tmp_path / "test.csv"
        _write_csv(csv_path, sample_labeled_data)

        loaded = load_labeled_data(csv_path)

        assert len(loaded) == 5
        assert loaded[0].comment_id == "c1"
        assert loaded[0].sentiment_label == 2
        assert loaded[0].is_relevant_label is True
        assert loaded[2].is_relevant_label is False

    def test_rejects_invalid_sentiment(self, tmp_path):
        csv_path = tmp_path / "bad.csv"
        csv_path.write_text(
            "comment_id,keyword,text,n_likes,post_text,difficulty,style,"
            "sentiment_label,is_relevant_label\n"
            "c1,test,text,0,post,easy,normal,5,TRUE\n",
            encoding="utf-8",
        )
        with pytest.raises((ValueError, TypeError)):
            load_labeled_data(csv_path)

    def test_rejects_invalid_difficulty(self, tmp_path):
        csv_path = tmp_path / "bad.csv"
        csv_path.write_text(
            "comment_id,keyword,text,n_likes,post_text,difficulty,style,"
            "sentiment_label,is_relevant_label\n"
            "c1,test,text,0,post,extreme,normal,0,TRUE\n",
            encoding="utf-8",
        )
        with pytest.raises((ValueError, TypeError)):
            load_labeled_data(csv_path)

    def test_handles_empty_file(self, tmp_path):
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text(
            "comment_id,keyword,text,n_likes,post_text,difficulty,style,sentiment_label,is_relevant_label\n",
            encoding="utf-8",
        )
        loaded = load_labeled_data(csv_path)
        assert loaded == []

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_labeled_data(tmp_path / "nonexistent.csv")


# ------------------------------------------------------------------ #
# Tests: Pure metric calculation functions
# ------------------------------------------------------------------ #


class TestMetricCalculation:
    def test_accuracy_exact_match(self):
        from src.m4_eval.run import _calc_group_accuracy
        # Just test the function directly with mock data
        samples = [
            LabeledSample(comment_id="c1", keyword="k", text="t", sentiment_label=1),
            LabeledSample(comment_id="c2", keyword="k", text="t", sentiment_label=2),
        ]
        results = [(samples[0], 1, True), (samples[1], 2, True)]
        acc_by_diff = _calc_group_accuracy(results, "difficulty")
        assert acc_by_diff["medium"] == 1.0  # default difficulty is "medium"

    def test_accuracy_partial_match(self):
        samples = [
            LabeledSample(comment_id="c1", keyword="k", text="t", sentiment_label=1),
            LabeledSample(comment_id="c2", keyword="k", text="t", sentiment_label=2),
            LabeledSample(comment_id="c3", keyword="k", text="t", sentiment_label=0),
        ]
        results = [(samples[0], 1, True), (samples[1], 2, True), (samples[2], 1, True)]
        acc_by_diff = _calc_group_accuracy(results, "difficulty")
        assert acc_by_diff["medium"] == pytest.approx(2 / 3)

    def test_f1_perfect(self):
        assert _calc_f1(tp=10, fp=0, fn=0) == 1.0

    def test_f1_zero_precision(self):
        assert _calc_f1(tp=0, fp=5, fn=0) == 0.0

    def test_f1_zero_recall(self):
        assert _calc_f1(tp=0, fp=0, fn=5) == 0.0

    def test_f1_edge_case_empty(self):
        assert _calc_f1(tp=0, fp=0, fn=0) == 0.0

    def test_f1_typical(self):
        # TP=3, FP=1, FN=2 -> P=3/4, R=3/5, F1=2*(3/4)*(3/5)/((3/4)+(3/5))=2*0.45/1.35≈0.667
        f1 = _calc_f1(tp=3, fp=1, fn=2)
        assert f1 == pytest.approx(2 * 0.75 * 0.6 / (0.75 + 0.6))


# ------------------------------------------------------------------ #
# Tests: Confusion matrix
# ------------------------------------------------------------------ #


class TestConfusionMatrix:
    def test_perfect_predictions(self):
        from src.m4_eval.run import _build_confusion_matrix
        samples = [
            LabeledSample(comment_id="c1", keyword="k", text="t", sentiment_label=1),
            LabeledSample(comment_id="c2", keyword="k", text="t", sentiment_label=-1),
        ]
        results = [(samples[0], 1, True), (samples[1], -1, True)]
        matrix = _build_confusion_matrix(results)
        assert matrix["1"]["1"] == 1
        assert matrix["-1"]["-1"] == 1

    def test_mixed_predictions(self):
        from src.m4_eval.run import _build_confusion_matrix
        samples = [
            LabeledSample(comment_id="c1", keyword="k", text="t", sentiment_label=1),
            LabeledSample(comment_id="c2", keyword="k", text="t", sentiment_label=1),
        ]
        results = [(samples[0], 1, True), (samples[1], -1, True)]
        matrix = _build_confusion_matrix(results)
        assert matrix["1"]["1"] == 1
        assert matrix["1"]["-1"] == 1


# ------------------------------------------------------------------ #
# Tests: Prompt versioning
# ------------------------------------------------------------------ #


class TestPromptVersioning:
    def test_v1_uses_default_prompts(self):
        path = _resolve_prompts_path("v1")
        assert path == Path("config/prompts.yaml")

    def test_unknown_version_raises(self):
        with pytest.raises(FileNotFoundError, match="v99"):
            _resolve_prompts_path("v99")

    def test_custom_prompt_id(self, tmp_path):
        custom = tmp_path / "v2.yaml"
        custom.write_text("per_comment:\n  system: test\n  user: test\n", encoding="utf-8")

        with patch("src.m4_eval.run.Path") as mock_path:
            # Make Path("config/eval_prompts/v2.yaml") resolve to our tmp file
            def _path_factory(p):
                if p == "config/eval_prompts/v2.yaml":
                    return custom
                return Path(p)
            mock_path.side_effect = _path_factory
            result = _resolve_prompts_path("v2")
            assert result == custom


# ------------------------------------------------------------------ #
# Tests: evaluate()
# ------------------------------------------------------------------ #


class TestEvaluate:
    def _prepare_csv(self, tmp_path, samples):
        csv_path = tmp_path / "labeled.csv"
        _write_csv(csv_path, samples)
        return csv_path

    def test_accuracy_calculation(self, tmp_path, sample_labeled_data):
        """3/5 correct predictions -> accuracy = 0.6"""
        csv_path = self._prepare_csv(tmp_path, sample_labeled_data)
        output_dir = tmp_path / "output"

        # Mock SentimentEngine.analyze to avoid LLM calls entirely.
        predictions = [
            (2, True),   # c1: correct (label=2)
            (0, True),   # c2: wrong (label=-1)
            (0, False),  # c3: correct (label=0, relevant=False)
            (0, False),  # c4: correct (label=0, relevant=False)
            (-1, True),  # c5: wrong (label=-2)
        ]

        call_idx = 0

        def _mock_analyze(self_engine, post):
            nonlocal call_idx
            sent, rel = predictions[call_idx]
            call_idx += 1
            return ScoredPost(
                post_id=post.post_id, keyword=post.keyword, date=date.today(),
                is_relevant=True, sentiment_post=0,
                comment_scores=[CommentScore(
                    comment_id=post.comments[0].comment_id, sentiment=sent, is_relevant=rel,
                )],
                n_comments_scored=1, sentiment_comments_avg=float(sent),
                sentiment_comments_std=0.0, fomo=0, quote="", model="test-model", cost_usd=0.001,
            )

        with patch.object(SentimentEngine, "analyze", _mock_analyze):
            report = evaluate(
                model="test-model", prompt_id="v1",
                labeled_path=csv_path, output_dir=output_dir,
            )

        assert report.accuracy == pytest.approx(0.6)
        assert report.total_samples == 5

    def test_accuracy_by_style(self, tmp_path, sample_labeled_data):
        csv_path = self._prepare_csv(tmp_path, sample_labeled_data)
        output_dir = tmp_path / "output"

        predictions = [
            (2, True), (-1, True), (0, False), (0, False), (-2, True),
        ]

        call_idx = 0

        def _mock_analyze(self_engine, post):
            nonlocal call_idx
            sent, rel = predictions[call_idx]
            call_idx += 1
            return ScoredPost(
                post_id=post.post_id, keyword=post.keyword, date=date.today(),
                is_relevant=True, sentiment_post=0,
                comment_scores=[CommentScore(
                    comment_id=post.comments[0].comment_id, sentiment=sent, is_relevant=rel,
                )],
                n_comments_scored=1, sentiment_comments_avg=float(sent),
                sentiment_comments_std=0.0, fomo=0, quote="", model="test-model", cost_usd=0.0,
            )

        with patch.object(SentimentEngine, "analyze", _mock_analyze):
            report = evaluate(
                model="test-model", prompt_id="v1",
                labeled_path=csv_path, output_dir=output_dir,
            )

        assert report.accuracy_by_style["normal"] == pytest.approx(1.0)
        assert report.accuracy_by_style["sarcasm"] == pytest.approx(1.0)
        assert report.accuracy_by_style["novice"] == pytest.approx(1.0)

    def test_sarcasm_subset_accuracy(self, tmp_path, sample_labeled_data):
        csv_path = self._prepare_csv(tmp_path, sample_labeled_data)
        output_dir = tmp_path / "output"

        # c2 (sarcasm, label=-1) predicted wrong as 0
        predictions = [
            (2, True), (0, True), (0, False), (0, False), (-2, True),
        ]

        call_idx = 0

        def _mock_analyze(self_engine, post):
            nonlocal call_idx
            sent, rel = predictions[call_idx]
            call_idx += 1
            return ScoredPost(
                post_id=post.post_id, keyword=post.keyword, date=date.today(),
                is_relevant=True, sentiment_post=0,
                comment_scores=[CommentScore(
                    comment_id=post.comments[0].comment_id, sentiment=sent, is_relevant=rel,
                )],
                n_comments_scored=1, sentiment_comments_avg=float(sent),
                sentiment_comments_std=0.0, fomo=0, quote="", model="test-model", cost_usd=0.0,
            )

        with patch.object(SentimentEngine, "analyze", _mock_analyze):
            report = evaluate(
                model="test-model", prompt_id="v1",
                labeled_path=csv_path, output_dir=output_dir,
            )

        assert report.sarcasm_subset_accuracy == pytest.approx(0.0)

    def test_is_relevant_f1(self, tmp_path, sample_labeled_data):
        csv_path = self._prepare_csv(tmp_path, sample_labeled_data)
        output_dir = tmp_path / "output"

        # Labels: c1=True, c2=True, c3=False, c4=False, c5=True
        # Predicted: all correct
        predictions = [
            (2, True), (-1, True), (0, False), (0, False), (-2, True),
        ]

        call_idx = 0

        def _mock_analyze(self_engine, post):
            nonlocal call_idx
            sent, rel = predictions[call_idx]
            call_idx += 1
            return ScoredPost(
                post_id=post.post_id, keyword=post.keyword, date=date.today(),
                is_relevant=True, sentiment_post=0,
                comment_scores=[CommentScore(
                    comment_id=post.comments[0].comment_id, sentiment=sent, is_relevant=rel,
                )],
                n_comments_scored=1, sentiment_comments_avg=float(sent),
                sentiment_comments_std=0.0, fomo=0, quote="", model="test-model", cost_usd=0.0,
            )

        with patch.object(SentimentEngine, "analyze", _mock_analyze):
            report = evaluate(
                model="test-model", prompt_id="v1",
                labeled_path=csv_path, output_dir=output_dir,
            )

        assert report.is_relevant_f1 == pytest.approx(1.0)

    def test_confusion_matrix_structure(self, tmp_path, sample_labeled_data):
        csv_path = self._prepare_csv(tmp_path, sample_labeled_data)
        output_dir = tmp_path / "output"

        predictions = [
            (2, True), (0, True), (0, False), (0, False), (-1, True),
        ]

        call_idx = 0

        def _mock_analyze(self_engine, post):
            nonlocal call_idx
            sent, rel = predictions[call_idx]
            call_idx += 1
            return ScoredPost(
                post_id=post.post_id, keyword=post.keyword, date=date.today(),
                is_relevant=True, sentiment_post=0,
                comment_scores=[CommentScore(
                    comment_id=post.comments[0].comment_id, sentiment=sent, is_relevant=rel,
                )],
                n_comments_scored=1, sentiment_comments_avg=float(sent),
                sentiment_comments_std=0.0, fomo=0, quote="", model="test-model", cost_usd=0.0,
            )

        with patch.object(SentimentEngine, "analyze", _mock_analyze):
            report = evaluate(
                model="test-model", prompt_id="v1",
                labeled_path=csv_path, output_dir=output_dir,
            )

        # c1: label=2, pred=2 -> matrix["2"]["2"] += 1
        # c5: label=-2, pred=-1 -> matrix["-2"]["-1"] += 1
        assert report.confusion_matrix["2"]["2"] == 1
        assert report.confusion_matrix["-2"]["-1"] == 1

    def test_report_has_correct_model_and_prompt_id(self, tmp_path, sample_labeled_data):
        csv_path = self._prepare_csv(tmp_path, sample_labeled_data)
        output_dir = tmp_path / "output"

        def _mock_analyze(self_engine, post):
            return ScoredPost(
                post_id=post.post_id, keyword=post.keyword, date=date.today(),
                is_relevant=True, sentiment_post=0,
                comment_scores=[CommentScore(
                    comment_id=post.comments[0].comment_id, sentiment=0, is_relevant=True,
                )],
                n_comments_scored=1, sentiment_comments_avg=0.0,
                sentiment_comments_std=0.0, fomo=0, quote="", model="my-model", cost_usd=0.0,
            )

        with patch.object(SentimentEngine, "analyze", _mock_analyze):
            report = evaluate(
                model="my-model", prompt_id="v1",
                labeled_path=csv_path, output_dir=output_dir,
            )

        assert report.model == "my-model"
        assert report.prompt_id == "v1"

    def test_total_cost_tracking(self, tmp_path, sample_labeled_data):
        csv_path = self._prepare_csv(tmp_path, sample_labeled_data)
        output_dir = tmp_path / "output"

        def _mock_analyze(self_engine, post):
            self_engine._total_cost_usd += 0.002
            return ScoredPost(
                post_id=post.post_id, keyword=post.keyword, date=date.today(),
                is_relevant=True, sentiment_post=0,
                comment_scores=[CommentScore(
                    comment_id=post.comments[0].comment_id, sentiment=0, is_relevant=True,
                )],
                n_comments_scored=1, sentiment_comments_avg=0.0,
                sentiment_comments_std=0.0, fomo=0, quote="", model="test", cost_usd=0.002,
            )

        with patch.object(SentimentEngine, "analyze", _mock_analyze):
            report = evaluate(
                model="test", prompt_id="v1",
                labeled_path=csv_path, output_dir=output_dir,
            )

        assert report.total_cost_usd == pytest.approx(0.01)

    def test_writes_results_csv(self, tmp_path, sample_labeled_data):
        csv_path = self._prepare_csv(tmp_path, sample_labeled_data)
        output_dir = tmp_path / "output"

        def _mock_analyze(self_engine, post):
            return ScoredPost(
                post_id=post.post_id, keyword=post.keyword, date=date.today(),
                is_relevant=True, sentiment_post=0,
                comment_scores=[CommentScore(
                    comment_id=post.comments[0].comment_id, sentiment=0, is_relevant=True,
                )],
                n_comments_scored=1, sentiment_comments_avg=0.0,
                sentiment_comments_std=0.0, fomo=0, quote="", model="test", cost_usd=0.0,
            )

        with patch.object(SentimentEngine, "analyze", _mock_analyze):
            evaluate(
                model="test", prompt_id="v1",
                labeled_path=csv_path, output_dir=output_dir,
            )

        # Check results CSV was written
        result_files = list(output_dir.glob("results_*.csv"))
        assert len(result_files) == 1

        # Check markdown report was written
        md_files = list(output_dir.glob("results_*.md"))
        assert len(md_files) == 1

    def test_empty_labeled_data_raises(self, tmp_path):
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text(
            "comment_id,keyword,text,n_likes,post_text,difficulty,style,sentiment_label,is_relevant_label\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="No labeled samples"):
            evaluate(model="test", prompt_id="v1", labeled_path=csv_path)


# ------------------------------------------------------------------ #
# Tests: Report generation
# ------------------------------------------------------------------ #


class TestReportGeneration:
    def test_markdown_contains_kpi_thresholds(self):
        report = EvalReport(
            model="test", prompt_id="v1", total_samples=200,
            accuracy=0.80, accuracy_by_difficulty={}, accuracy_by_style={},
            sarcasm_subset_accuracy=0.75, is_relevant_f1=0.90,
            confusion_matrix={}, total_cost_usd=0.5, run_date="2026-05-23",
        )
        md = _generate_markdown_report(report, Path("data/eval/results.csv"))
        assert "75%" in md
        assert "70%" in md
        assert "0.85" in md

    def test_markdown_contains_confusion_matrix(self):
        report = EvalReport(
            model="test", prompt_id="v1", total_samples=2,
            accuracy=1.0, accuracy_by_difficulty={}, accuracy_by_style={},
            sarcasm_subset_accuracy=0.0, is_relevant_f1=1.0,
            confusion_matrix={"1": {"1": 2}}, total_cost_usd=0.0, run_date="2026-05-23",
        )
        md = _generate_markdown_report(report, Path("results.csv"))
        assert "Confusion Matrix" in md
        assert "1" in md

    def test_markdown_contains_model_name(self):
        report = EvalReport(
            model="gpt-4o-mini", prompt_id="v2", total_samples=10,
            accuracy=0.5, accuracy_by_difficulty={}, accuracy_by_style={},
            sarcasm_subset_accuracy=0.0, is_relevant_f1=0.5,
            confusion_matrix={}, total_cost_usd=0.1, run_date="2026-05-23",
        )
        md = _generate_markdown_report(report, Path("results.csv"))
        assert "gpt-4o-mini" in md
        assert "v2" in md

    def test_kpi_pass_status(self):
        report = EvalReport(
            model="test", prompt_id="v1", total_samples=200,
            accuracy=0.80, accuracy_by_difficulty={}, accuracy_by_style={},
            sarcasm_subset_accuracy=0.75, is_relevant_f1=0.90,
            confusion_matrix={}, total_cost_usd=0.5, run_date="2026-05-23",
        )
        md = _generate_markdown_report(report, Path("results.csv"))
        assert md.count("PASS") >= 3

    def test_kpi_fail_status(self):
        report = EvalReport(
            model="test", prompt_id="v1", total_samples=200,
            accuracy=0.50, accuracy_by_difficulty={}, accuracy_by_style={},
            sarcasm_subset_accuracy=0.50, is_relevant_f1=0.50,
            confusion_matrix={}, total_cost_usd=0.5, run_date="2026-05-23",
        )
        md = _generate_markdown_report(report, Path("results.csv"))
        assert md.count("FAIL") >= 3
