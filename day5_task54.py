"""Task 5.4 - Detection metrics for one image and one object class."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import isfinite
from numbers import Real
from pathlib import Path
from typing import Sequence

from day5_task52 import Box, BoxFormat, box_to_xyxy, iou
from day5_task53 import nms


@dataclass(frozen=True)
class DetectionMetrics:
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    matches: tuple[tuple[int, int], ...]


DEFAULT_MAP_IOU_THRESHOLDS = tuple(value / 100 for value in range(50, 100, 5))


def evaluate_detections(
    pred_boxes: Sequence[Box],
    scores: Sequence[Real],
    gt_boxes: Sequence[Box],
    iou_threshold: float = 0.5,
    box_format: BoxFormat = "xyxy",
) -> DetectionMetrics:
    """Evaluate one image/class, matching predictions by score to unmatched GT.

    Each prediction is matched to its highest-IoU unmatched ground truth when
    that IoU is at least the threshold. Ties in prediction score keep input order.
    """
    if len(pred_boxes) != len(scores):
        raise ValueError("pred_boxes and scores must have the same length")
    if box_format not in ("xywh", "xyxy"):
        raise ValueError("box_format must be 'xywh' or 'xyxy'")
    if not isinstance(iou_threshold, Real) or not isfinite(float(iou_threshold)):
        raise ValueError("iou_threshold must be a finite number between 0 and 1")
    iou_threshold = float(iou_threshold)
    if not 0 <= iou_threshold <= 1:
        raise ValueError("iou_threshold must be between 0 and 1")

    for box in (*pred_boxes, *gt_boxes):
        box_to_xyxy(box, box_format)

    score_values: list[float] = []
    for score in scores:
        if not isinstance(score, Real) or not isfinite(float(score)):
            raise ValueError("scores must be finite real numbers")
        score_value = float(score)
        if score_value < 0:
            raise ValueError("scores must not be negative")
        score_values.append(score_value)

    unmatched_gt = set(range(len(gt_boxes)))
    matches: list[tuple[int, int]] = []
    false_positives = 0

    for pred_idx in sorted(range(len(pred_boxes)), key=lambda idx: (-score_values[idx], idx)):
        best_gt_idx: int | None = None
        best_iou = -1.0
        for gt_idx in sorted(unmatched_gt):
            overlap = iou(pred_boxes[pred_idx], gt_boxes[gt_idx], box_format)
            if overlap > best_iou:
                best_iou = overlap
                best_gt_idx = gt_idx

        if best_gt_idx is not None and best_iou >= iou_threshold:
            unmatched_gt.remove(best_gt_idx)
            matches.append((pred_idx, best_gt_idx))
        else:
            false_positives += 1

    true_positives = len(matches)
    false_negatives = len(unmatched_gt)
    precision = true_positives / len(pred_boxes) if pred_boxes else 0.0
    recall = true_positives / len(gt_boxes) if gt_boxes else 0.0
    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return DetectionMetrics(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        matches=tuple(matches),
    )


def average_precision(
    pred_boxes: Sequence[Box],
    scores: Sequence[Real],
    gt_boxes: Sequence[Box],
    iou_threshold: float = 0.5,
    box_format: BoxFormat = "xyxy",
    recall_points: int = 101,
) -> float:
    """Calculate 101-point interpolated AP for one image and one class.

    Predictions are ranked by score. AP is undefined without ground-truth
    objects, so that input raises ValueError.
    """
    if not isinstance(recall_points, int) or recall_points < 2:
        raise ValueError("recall_points must be an integer of at least 2")
    if not gt_boxes:
        raise ValueError("average precision is undefined without ground truths")

    metrics = evaluate_detections(
        pred_boxes, scores, gt_boxes, iou_threshold, box_format
    )
    matched_predictions = {pred_idx for pred_idx, _ in metrics.matches}
    score_values = [float(score) for score in scores]
    ordered_predictions = sorted(
        range(len(pred_boxes)), key=lambda idx: (-score_values[idx], idx)
    )
    if not ordered_predictions:
        return 0.0

    cumulative_true_positives = 0
    cumulative_false_positives = 0
    precision_recall_points: list[tuple[float, float]] = []
    for pred_idx in ordered_predictions:
        if pred_idx in matched_predictions:
            cumulative_true_positives += 1
        else:
            cumulative_false_positives += 1
        recall = cumulative_true_positives / len(gt_boxes)
        precision = cumulative_true_positives / (
            cumulative_true_positives + cumulative_false_positives
        )
        precision_recall_points.append((recall, precision))

    interpolated_precisions = []
    for point in range(recall_points):
        target_recall = point / (recall_points - 1)
        interpolated_precisions.append(
            max(
                (
                    precision
                    for recall, precision in precision_recall_points
                    if recall >= target_recall
                ),
                default=0.0,
            )
        )
    return sum(interpolated_precisions) / recall_points


def mean_average_precision(
    pred_boxes: Sequence[Box],
    scores: Sequence[Real],
    gt_boxes: Sequence[Box],
    iou_thresholds: Sequence[float] = DEFAULT_MAP_IOU_THRESHOLDS,
    box_format: BoxFormat = "xyxy",
) -> float:
    """Average AP over IoU thresholds for this single-class evaluation.

    With one class, class-averaging is trivial; the default thresholds produce
    the COCO-style mAP50-95 value for one image and one class.
    """
    if not iou_thresholds:
        raise ValueError("iou_thresholds must not be empty")
    aps = [
        average_precision(
            pred_boxes,
            scores,
            gt_boxes,
            iou_threshold=threshold,
            box_format=box_format,
        )
        for threshold in iou_thresholds
    ]
    return sum(aps) / len(aps)


def build_demo_report() -> dict[str, object]:
    """Build a reproducible IoU, NMS and detection-metrics report."""
    ground_truths = [
        (20, 20, 120, 120),
        (150, 25, 230, 105),
        (270, 20, 370, 120),
        (400, 30, 490, 120),
    ]
    predictions = [
        (22, 22, 118, 118),
        (150, 25, 230, 105),
        (25, 25, 115, 115),
        (275, 25, 365, 115),
        (520, 200, 580, 260),
    ]
    scores = [0.98, 0.92, 0.80, 0.74, 0.45]
    threshold = 0.5
    overlaps = [
        [iou(pred, truth) for truth in ground_truths]
        for pred in predictions
    ]
    metrics_before_nms = evaluate_detections(
        predictions, scores, ground_truths, iou_threshold=threshold
    )
    kept_indices = nms(predictions, scores, threshold=0.5)
    predictions_after_nms = [predictions[index] for index in kept_indices]
    scores_after_nms = [scores[index] for index in kept_indices]
    metrics_after_nms = evaluate_detections(
        predictions_after_nms,
        scores_after_nms,
        ground_truths,
        iou_threshold=threshold,
    )

    def metric_report(
        metrics: DetectionMetrics,
        boxes: Sequence[Box],
        report_scores: Sequence[Real],
    ) -> dict[str, object]:
        return {
            **asdict(metrics),
            "ap50": average_precision(
                boxes, report_scores, ground_truths, iou_threshold=0.5
            ),
            "map50_95": mean_average_precision(
                boxes, report_scores, ground_truths
            ),
        }

    return {
        "scope": "one image, one class, synthetic axis-aligned boxes",
        "iou_threshold": threshold,
        "ground_truth_boxes_xyxy": ground_truths,
        "predictions": [
            {"box_xyxy": box, "score": score}
            for box, score in zip(predictions, scores)
        ],
        "iou_matrix": overlaps,
        "nms": {
            "threshold": 0.5,
            "kept_indices": kept_indices,
            "suppressed_indices": [
                index for index in range(len(predictions)) if index not in kept_indices
            ],
        },
        "metrics_before_nms": metric_report(
            metrics_before_nms, predictions, scores
        ),
        "metrics_after_nms": metric_report(
            metrics_after_nms, predictions_after_nms, scores_after_nms
        ),
        "metric_definitions": {
            "precision": "TP / (TP + FP)",
            "recall": "TP / (TP + FN)",
            "f1_score": "2 * precision * recall / (precision + recall)",
            "ap50": "101-point interpolated AP at IoU 0.50",
            "map50_95": "mean AP at IoU thresholds 0.50 to 0.95 by 0.05",
        },
        "evaluation_scope": "Metrics are shown both before and after NMS.",
    }


def write_demo_report(output_path: str | Path) -> Path:
    """Write the synthetic evaluation report as UTF-8 JSON."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(build_demo_report(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return destination


def main() -> int:
    output_path = Path("outputs/task54/detection_report.json")
    report = build_demo_report()
    write_demo_report(output_path)
    print(f"Evaluation report saved to: {output_path}")
    print("Metrics before NMS:")
    print(json.dumps(report["metrics_before_nms"], indent=2))
    print("Metrics after NMS:")
    print(json.dumps(report["metrics_after_nms"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
