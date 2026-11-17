"""Task 5.3 - Hard Non-Maximum Suppression for axis-aligned boxes."""

from __future__ import annotations

from math import isfinite
from numbers import Real
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np

from day5_task52 import Box, BoxFormat, box_to_xyxy, iou


def _validate_inputs(
    boxes: Sequence[Box],
    scores: Sequence[Real],
    threshold: float,
    box_format: BoxFormat,
) -> list[float]:
    if len(boxes) != len(scores):
        raise ValueError("boxes and scores must have the same length")
    if box_format not in ("xywh", "xyxy"):
        raise ValueError("box_format must be 'xywh' or 'xyxy'")
    if not isinstance(threshold, Real) or not isfinite(float(threshold)):
        raise ValueError("threshold must be a finite number between 0 and 1")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")

    for box in boxes:
        box_to_xyxy(box, box_format)

    validated_scores: list[float] = []
    for score in scores:
        if not isinstance(score, Real) or not isfinite(float(score)):
            raise ValueError("scores must be finite real numbers")
        score_value = float(score)
        if score_value < 0:
            raise ValueError("scores must not be negative")
        validated_scores.append(score_value)
    return validated_scores


def nms(
    boxes: Sequence[Box],
    scores: Sequence[Real],
    threshold: float = 0.5,
    box_format: BoxFormat = "xyxy",
) -> list[int]:
    """Keep box indices in descending score order using hard NMS.

    A lower-scored box is suppressed only when its IoU with a kept box is
    strictly greater than threshold. Equal scores are ordered by input index.
    """
    validated_scores = _validate_inputs(boxes, scores, threshold, box_format)
    candidates = sorted(range(len(boxes)), key=lambda index: (-validated_scores[index], index))
    kept: list[int] = []

    while candidates:
        current = candidates.pop(0)
        kept.append(current)
        candidates = [
            index
            for index in candidates
            if iou(boxes[current], boxes[index], box_format) <= threshold
        ]
    return kept


def nms_with_scores(
    boxes: Sequence[Box],
    scores: Sequence[Real],
    threshold: float = 0.5,
    box_format: BoxFormat = "xyxy",
) -> list[tuple[int, float]]:
    """Return kept original indices paired with their input scores."""
    validated_scores = _validate_inputs(boxes, scores, threshold, box_format)
    kept_indices = nms(boxes, validated_scores, threshold, box_format)
    return [(index, validated_scores[index]) for index in kept_indices]


def demo(output_path: str | Path = "outputs/task53/task53_nms.png") -> list[int]:
    """Run NMS on five overlapping synthetic boxes and save a visualization."""
    boxes = [
        (40, 40, 140, 140),
        (45, 45, 145, 145),
        (50, 50, 150, 150),
        (55, 55, 155, 155),
        (60, 60, 160, 160),
    ]
    scores = [0.95, 0.90, 0.85, 0.80, 0.75]
    threshold = 0.45
    kept_indices = nms(boxes, scores, threshold, box_format="xyxy")

    image = np.full((210, 210, 3), 255, dtype=np.uint8)
    kept_set = set(kept_indices)
    for index, (x1, y1, x2, y2) in enumerate(boxes):
        color = (0, 160, 0) if index in kept_set else (0, 0, 220)
        thickness = 3 if index in kept_set else 1
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
        cv2.putText(
            image,
            f"{index}: {scores[index]:.2f}",
            (x1, max(18, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            1,
            cv2.LINE_AA,
        )

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(destination), image):
        raise OSError(f"Could not write NMS visualization to {destination}")
    print(f"Kept indices: {kept_indices}")
    print(f"Visualization saved to: {destination}")
    return kept_indices


if __name__ == "__main__":
    demo()
