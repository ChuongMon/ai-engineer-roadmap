from pathlib import Path

import cv2
import numpy as np
import pytest

from day5_task53 import demo, nms, nms_with_scores


def test_nms_keeps_highest_score_among_five_overlapping_boxes() -> None:
    boxes = [
        (0, 0, 100, 100),
        (5, 5, 105, 105),
        (10, 10, 110, 110),
        (15, 15, 115, 115),
        (20, 20, 120, 120),
    ]
    scores = [0.9, 0.8, 0.7, 0.6, 0.5]

    assert nms(boxes, scores, threshold=0.4) == [0]


def test_nms_keeps_non_overlapping_boxes() -> None:
    boxes = [(0, 0, 10, 10), (20, 20, 30, 30), (40, 40, 50, 50)]

    assert nms(boxes, [0.4, 0.9, 0.6], threshold=0.5) == [1, 2, 0]


def test_lower_threshold_suppresses_more_boxes() -> None:
    boxes = [(0, 0, 100, 100), (25, 0, 125, 100), (50, 0, 150, 100)]
    scores = [0.9, 0.8, 0.7]

    assert len(nms(boxes, scores, threshold=0.1)) < len(
        nms(boxes, scores, threshold=0.7)
    )


def test_nms_empty_input_returns_empty_list() -> None:
    assert nms([], [], threshold=0.5) == []


def test_nms_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        nms([(0, 0, 10, 10)], [], threshold=0.5)


@pytest.mark.parametrize("score", [-0.1, float("nan"), float("inf")])
def test_nms_rejects_negative_or_non_finite_scores(score: float) -> None:
    with pytest.raises(ValueError, match="scores"):
        nms([(0, 0, 10, 10)], [score], threshold=0.5)


def test_nms_returns_original_indices_in_score_order() -> None:
    boxes = [(0, 0, 10, 10), (20, 20, 30, 30), (40, 40, 50, 50)]

    assert nms(boxes, [0.2, 0.9, 0.7], threshold=0.5) == [1, 2, 0]


def test_nms_breaks_score_ties_by_original_index() -> None:
    boxes = [(0, 0, 10, 10), (20, 20, 30, 30)]

    assert nms(boxes, [0.5, 0.5], threshold=0.5) == [0, 1]


def test_nms_supports_xywh_format() -> None:
    boxes_xywh = [(0, 0, 10, 10), (1, 1, 10, 10)]
    boxes_xyxy = [(0, 0, 10, 10), (1, 1, 11, 11)]

    assert nms(boxes_xywh, [0.9, 0.8], 0.5, "xywh") == nms(
        boxes_xyxy, [0.9, 0.8], 0.5, "xyxy"
    )


def test_box_at_exact_threshold_is_not_suppressed() -> None:
    boxes = [(0, 0, 10, 10), (0, 0, 5, 10)]

    assert nms(boxes, [0.9, 0.8], threshold=0.5) == [0, 1]


def test_nms_rejects_invalid_threshold_and_box() -> None:
    with pytest.raises(ValueError, match="threshold"):
        nms([], [], threshold=1.1)
    with pytest.raises(ValueError, match="reversed"):
        nms([(0, 0, -1, 10)], [0.9])


def test_nms_with_scores_returns_indices_and_original_scores() -> None:
    boxes = [(0, 0, 10, 10), (20, 20, 30, 30)]

    assert nms_with_scores(boxes, [0.3, 0.8]) == [(1, 0.8), (0, 0.3)]


def test_demo_saves_visualization(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "nms.png"

    kept = demo(output_path)

    assert kept == [0]
    assert cv2.imread(str(output_path)) is not None
    assert np.asarray(cv2.imread(str(output_path))).shape == (210, 210, 3)
