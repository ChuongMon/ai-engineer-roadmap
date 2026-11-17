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
    metrics = evaluate_detections(
        predictions, scores, ground_truths, iou_threshold=threshold
    )
    kept_indices = nms(predictions, scores, threshold=0.5)

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
        "metrics": asdict(metrics),
        "metric_definitions": {
            "precision": "TP / (TP + FP)",
            "recall": "TP / (TP + FN)",
            "f1_score": "2 * precision * recall / (precision + recall)",
        },
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
    metrics = report["metrics"]
    print(f"Evaluation report saved to: {output_path}")
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
