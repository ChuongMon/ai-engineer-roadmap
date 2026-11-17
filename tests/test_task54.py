import json
from pathlib import Path

import pytest

from day5_task54 import (
    average_precision,
    build_demo_report,
    evaluate_detections,
    mean_average_precision,
    write_demo_report,
)


def test_evaluation_counts_true_false_positives_and_false_negatives() -> None:
    ground_truths = [(0, 0, 10, 10), (20, 20, 30, 30)]
    predictions = [(1, 1, 9, 9), (0, 0, 10, 10), (40, 40, 50, 50)]
    scores = [0.9, 0.8, 0.7]

    metrics = evaluate_detections(predictions, scores, ground_truths)

    assert (metrics.true_positives, metrics.false_positives, metrics.false_negatives) == (
        1,
        2,
        1,
    )
    assert metrics.matches == ((0, 0),)


def test_evaluation_calculates_precision_recall_and_f1() -> None:
    metrics = evaluate_detections(
        [(0, 0, 10, 10), (20, 20, 30, 30)],
        [0.9, 0.8],
        [(0, 0, 10, 10), (40, 40, 50, 50)],
    )

    assert metrics.precision == pytest.approx(0.5)
    assert metrics.recall == pytest.approx(0.5)
    assert metrics.f1_score == pytest.approx(0.5)


def test_evaluation_matches_predictions_in_score_order() -> None:
    metrics = evaluate_detections(
        [(0, 0, 10, 10), (20, 20, 30, 30)],
        [0.4, 0.9],
        [(0, 0, 10, 10), (20, 20, 30, 30)],
    )

    assert metrics.matches == ((1, 1), (0, 0))


def test_duplicate_prediction_is_false_positive() -> None:
    metrics = evaluate_detections(
        [(0, 0, 10, 10), (0, 0, 10, 10)],
        [0.9, 0.8],
        [(0, 0, 10, 10)],
    )

    assert metrics.true_positives == 1
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 0


def test_evaluation_uses_iou_threshold() -> None:
    metrics = evaluate_detections(
        [(0, 0, 5, 10)],
        [0.9],
        [(0, 0, 10, 10)],
        iou_threshold=0.6,
    )

    assert (metrics.true_positives, metrics.false_positives, metrics.false_negatives) == (
        0,
        1,
        1,
    )


def test_empty_predictions_and_ground_truth_have_zero_metrics() -> None:
    metrics = evaluate_detections([], [], [])

    assert metrics.true_positives == 0
    assert metrics.false_positives == 0
    assert metrics.false_negatives == 0
    assert metrics.precision == metrics.recall == metrics.f1_score == 0.0


def test_no_predictions_gives_zero_precision_and_recall() -> None:
    metrics = evaluate_detections([], [], [(0, 0, 10, 10)])

    assert metrics.false_negatives == 1
    assert metrics.precision == metrics.recall == metrics.f1_score == 0.0


def test_no_ground_truth_predictions_are_false_positives() -> None:
    metrics = evaluate_detections([(0, 0, 10, 10)], [0.9], [])

    assert metrics.false_positives == 1
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0


def test_evaluation_supports_xywh() -> None:
    metrics = evaluate_detections(
        [(0, 0, 10, 10)],
        [0.9],
        [(0, 0, 10, 10)],
        box_format="xywh",
    )

    assert metrics.true_positives == 1


def test_average_precision_is_one_for_perfect_detections() -> None:
    boxes = [(0, 0, 10, 10), (20, 20, 30, 30)]

    assert average_precision(boxes, [0.9, 0.8], boxes) == pytest.approx(1.0)


def test_average_precision_accounts_for_high_score_false_positive() -> None:
    gt_boxes = [(0, 0, 10, 10)]
    pred_boxes = [(20, 20, 30, 30), (0, 0, 10, 10)]

    assert average_precision(pred_boxes, [0.9, 0.8], gt_boxes) == pytest.approx(0.5)


def test_average_precision_is_zero_without_predictions() -> None:
    assert average_precision([], [], [(0, 0, 10, 10)]) == 0.0


def test_average_precision_requires_ground_truths() -> None:
    with pytest.raises(ValueError, match="ground truths"):
        average_precision([(0, 0, 10, 10)], [0.9], [])


def test_mean_average_precision_averages_iou_thresholds() -> None:
    boxes = [(0, 0, 10, 10)]

    assert mean_average_precision(boxes, [0.9], boxes) == pytest.approx(1.0)
    assert mean_average_precision(
        [(0, 0, 5, 10)],
        [0.9],
        boxes,
        iou_thresholds=[0.5, 0.75],
    ) == pytest.approx(0.5)
    with pytest.raises(ValueError, match="must not be empty"):
        mean_average_precision(boxes, [0.9], boxes, iou_thresholds=[])


def test_average_precision_rejects_too_few_recall_points() -> None:
    with pytest.raises(ValueError, match="recall_points"):
        average_precision(
            [(0, 0, 10, 10)],
            [0.9],
            [(0, 0, 10, 10)],
            recall_points=1,
        )


@pytest.mark.parametrize(
    "predictions, scores, ground_truths, threshold",
    [
        ([(0, 0, 1, 1)], [], [], 0.5),
        ([], [], [], -0.1),
        ([], [], [], 1.1),
        ([(0, 0, 1, 1)], [float("nan")], [], 0.5),
        ([(0, 0, 1, 1)], [-1], [], 0.5),
    ],
)
def test_evaluation_rejects_invalid_inputs(
    predictions: list[tuple],
    scores: list[float],
    ground_truths: list[tuple],
    threshold: float,
) -> None:
    with pytest.raises(ValueError):
        evaluate_detections(
            predictions, scores, ground_truths, iou_threshold=threshold
        )


def test_demo_report_contains_iou_nms_and_detection_metrics() -> None:
    report = build_demo_report()
    before_nms = report["metrics_before_nms"]
    after_nms = report["metrics_after_nms"]

    assert len(report["iou_matrix"]) == len(report["predictions"])
    assert report["nms"]["kept_indices"]
    assert report["evaluation_scope"].endswith("before and after NMS.")
    assert before_nms["true_positives"] == 3
    assert before_nms["false_positives"] == 2
    assert before_nms["false_negatives"] == 1
    assert before_nms["precision"] == pytest.approx(0.6)
    assert before_nms["recall"] == pytest.approx(0.75)
    assert before_nms["ap50"] > 0
    assert 0 <= before_nms["map50_95"] <= 1
    assert after_nms["true_positives"] == 3
    assert after_nms["false_positives"] == 1
    assert after_nms["false_negatives"] == 1
    assert after_nms["precision"] == pytest.approx(0.75)
    assert after_nms["recall"] == pytest.approx(0.75)


def test_write_demo_report_creates_json(tmp_path: Path) -> None:
    output_path = write_demo_report(tmp_path / "nested" / "report.json")

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["scope"].startswith("one image")
    assert data["metrics_before_nms"]["f1_score"] > 0
    assert data["metrics_after_nms"]["ap50"] > 0
