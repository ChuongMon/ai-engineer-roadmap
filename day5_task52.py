"""Task 5.2 - Axis-aligned Intersection over Union (IoU)."""

from __future__ import annotations

from math import isfinite
from numbers import Real
from typing import Literal, Sequence

import numpy as np
from numpy.typing import NDArray

BoxFormat = Literal["xywh", "xyxy"]
Box = Sequence[Real]


def box_to_xyxy(box: Box, box_format: BoxFormat) -> tuple[float, float, float, float]:
    """Validate a four-value box and normalize it to (x1, y1, x2, y2).

    Zero-width or zero-height boxes are valid, degenerate boxes. Negative sizes
    and reversed corners are invalid.
    """
    if box_format not in ("xywh", "xyxy"):
        raise ValueError("box_format must be 'xywh' or 'xyxy'")
    if isinstance(box, (str, bytes)):
        raise ValueError("box must contain exactly four numeric values")
    try:
        if len(box) != 4:
            raise ValueError("box must contain exactly four numeric values")
    except TypeError as exc:
        raise ValueError("box must contain exactly four numeric values") from exc
    if any(not isinstance(value, Real) for value in box):
        raise ValueError("box coordinates must be real numbers")

    try:
        x1, y1, value3, value4 = (float(value) for value in box)
    except OverflowError as exc:
        raise ValueError("box coordinates must be finite") from exc
    if not all(isfinite(value) for value in (x1, y1, value3, value4)):
        raise ValueError("box coordinates must be finite")

    if box_format == "xywh":
        width, height = value3, value4
        if width < 0 or height < 0:
            raise ValueError("box width and height must not be negative")
        x2, y2 = x1 + width, y1 + height
    else:
        x2, y2 = value3, value4
        if x2 < x1 or y2 < y1:
            raise ValueError("xyxy box corners must not be reversed")

    normalized = (x1, y1, x2, y2)
    if not all(isfinite(value) for value in normalized):
        raise ValueError("box coordinates must be finite")
    if not isfinite((x2 - x1) * (y2 - y1)):
        raise ValueError("box area must be finite")
    return normalized


def _area(box_xyxy: tuple[float, float, float, float]) -> float:
    x1, y1, x2, y2 = box_xyxy
    return (x2 - x1) * (y2 - y1)


def _intersection_area(
    box_a: tuple[float, float, float, float],
    box_b: tuple[float, float, float, float],
) -> float:
    left = max(box_a[0], box_b[0])
    top = max(box_a[1], box_b[1])
    right = min(box_a[2], box_b[2])
    bottom = min(box_a[3], box_b[3])
    return max(0.0, right - left) * max(0.0, bottom - top)


def intersection_area(
    box1: Box, box2: Box, box_format: BoxFormat = "xyxy"
) -> float:
    """Return the shared area of two axis-aligned boxes."""
    box_a = box_to_xyxy(box1, box_format)
    box_b = box_to_xyxy(box2, box_format)
    return _intersection_area(box_a, box_b)


def union_area(box1: Box, box2: Box, box_format: BoxFormat = "xyxy") -> float:
    """Return the total area covered by two axis-aligned boxes."""
    box_a = box_to_xyxy(box1, box_format)
    box_b = box_to_xyxy(box2, box_format)
    return _area(box_a) + _area(box_b) - _intersection_area(box_a, box_b)


def iou(box1: Box, box2: Box, box_format: BoxFormat = "xyxy") -> float:
    """Calculate IoU; return 0 when the union has zero area."""
    box_a = box_to_xyxy(box1, box_format)
    box_b = box_to_xyxy(box2, box_format)
    intersection = _intersection_area(box_a, box_b)
    union = _area(box_a) + _area(box_b) - intersection
    return intersection / union if union > 0 else 0.0


def iou_matrix(
    boxes1: Sequence[Box],
    boxes2: Sequence[Box],
    box_format: BoxFormat = "xyxy",
) -> NDArray[np.float64]:
    """Return an (N, M) matrix containing IoU for every pair of boxes."""
    normalized1 = [box_to_xyxy(box, box_format) for box in boxes1]
    normalized2 = [box_to_xyxy(box, box_format) for box in boxes2]
    matrix = np.zeros((len(normalized1), len(normalized2)), dtype=np.float64)

    for row, box_a in enumerate(normalized1):
        area_a = _area(box_a)
        for column, box_b in enumerate(normalized2):
            intersection = _intersection_area(box_a, box_b)
            union = area_a + _area(box_b) - intersection
            matrix[row, column] = intersection / union if union > 0 else 0.0
    return matrix


def match_boxes(
    pred_boxes: Sequence[Box],
    gt_boxes: Sequence[Box],
    threshold: float = 0.5,
    box_format: BoxFormat = "xyxy",
) -> list[tuple[int, int]]:
    """Greedily match boxes one-to-one, considering highest IoU pairs first.

    Ties are resolved by prediction index and then ground-truth index. This
    simple assignment is deterministic, but is not a globally optimal matcher.
    """
    if not isinstance(threshold, Real) or not isfinite(float(threshold)):
        raise ValueError("threshold must be a finite number between 0 and 1")
    threshold = float(threshold)
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")

    similarities = iou_matrix(pred_boxes, gt_boxes, box_format)
    candidates = [
        (float(similarities[pred_idx, gt_idx]), pred_idx, gt_idx)
        for pred_idx in range(similarities.shape[0])
        for gt_idx in range(similarities.shape[1])
        if similarities[pred_idx, gt_idx] >= threshold
    ]
    candidates.sort(key=lambda candidate: (-candidate[0], candidate[1], candidate[2]))

    matched_predictions: set[int] = set()
    matched_ground_truths: set[int] = set()
    matches: list[tuple[int, int]] = []
    for _, pred_idx, gt_idx in candidates:
        if pred_idx not in matched_predictions and gt_idx not in matched_ground_truths:
            matches.append((pred_idx, gt_idx))
            matched_predictions.add(pred_idx)
            matched_ground_truths.add(gt_idx)

    return sorted(matches)
