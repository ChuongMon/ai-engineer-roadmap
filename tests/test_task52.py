import numpy as np
import pytest

from day5_task52 import (
    box_to_xyxy,
    intersection_area,
    iou,
    iou_matrix,
    match_boxes,
    union_area,
)


def test_iou_self_equals_one() -> None:
    assert iou((1, 2, 11, 12), (1, 2, 11, 12)) == 1.0


def test_iou_non_overlapping_equals_zero() -> None:
    assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0


def test_partial_overlap_areas_and_iou_are_exact() -> None:
    first = (0, 0, 10, 10)
    second = (5, 5, 15, 15)

    assert intersection_area(first, second) == 25.0
    assert union_area(first, second) == 175.0
    assert iou(first, second) == pytest.approx(1 / 7)


def test_iou_contained_box_is_area_ratio() -> None:
    assert iou((0, 0, 10, 10), (2, 2, 4, 4)) == pytest.approx(0.04)


def test_xywh_and_xyxy_formats_produce_same_iou() -> None:
    assert iou((0, 0, 10, 10), (5, 5, 10, 10), "xywh") == pytest.approx(
        iou((0, 0, 10, 10), (5, 5, 15, 15), "xyxy")
    )


def test_box_to_xyxy_normalizes_xywh() -> None:
    assert box_to_xyxy((3, 4, 5, 6), "xywh") == (3.0, 4.0, 8.0, 10.0)


def test_iou_supports_negative_coordinates() -> None:
    assert iou((-5, -5, 5, 5), (0, 0, 10, 10)) == pytest.approx(25 / 175)


def test_zero_area_box_has_zero_iou() -> None:
    assert iou((2, 2, 2, 8), (0, 0, 10, 10)) == 0.0
    assert iou((2, 2, 2, 2), (2, 2, 2, 2)) == 0.0


@pytest.mark.parametrize(
    "box, box_format",
    [
        ((0, 0, -1, 2), "xywh"),
        ((0, 0, 2, -1), "xywh"),
        ((0, 0, -1, 2), "xyxy"),
        ((0, 0, 2, -1), "xyxy"),
        ((0, 0, float("nan"), 2), "xyxy"),
        ((0, 0, 1), "xyxy"),
    ],
)
def test_invalid_box_raises(box: tuple, box_format: str) -> None:
    with pytest.raises(ValueError):
        box_to_xyxy(box, box_format)  # type: ignore[arg-type]


def test_unknown_box_format_raises() -> None:
    with pytest.raises(ValueError, match="box_format"):
        box_to_xyxy((0, 0, 1, 1), "xywh2")  # type: ignore[arg-type]


def test_invalid_box_shape_and_overflow_raise() -> None:
    with pytest.raises(ValueError, match="four"):
        box_to_xyxy(10, "xyxy")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="finite"):
        box_to_xyxy((1e308, 0, 1e308, 1), "xywh")
    with pytest.raises(ValueError, match="area"):
        box_to_xyxy((0, 0, 1e308, 1e308), "xyxy")


def test_iou_matrix_has_expected_shape_and_values() -> None:
    matrix = iou_matrix(
        [(0, 0, 10, 10), (20, 20, 30, 30)],
        [(0, 0, 10, 10), (5, 5, 15, 15)],
    )

    assert matrix.shape == (2, 2)
    np.testing.assert_allclose(matrix, [[1.0, 25 / 175], [0.0, 0.0]])


def test_iou_matrix_preserves_empty_dimensions() -> None:
    assert iou_matrix([], [(0, 0, 1, 1)]).shape == (0, 1)
    assert iou_matrix([(0, 0, 1, 1)], []).shape == (1, 0)


def test_match_boxes_applies_threshold_and_is_one_to_one() -> None:
    predictions = [(0, 0, 10, 10), (1, 1, 11, 11), (30, 30, 40, 40)]
    ground_truths = [(0, 0, 10, 10), (20, 20, 30, 30)]

    assert match_boxes(predictions, ground_truths, threshold=0.5) == [(0, 0)]


def test_match_boxes_prefers_highest_iou_then_returns_index_order() -> None:
    predictions = [(0, 0, 10, 10), (1, 1, 11, 11)]
    ground_truths = [(0, 0, 10, 10), (1, 1, 11, 11)]

    assert match_boxes(predictions, ground_truths, threshold=0.5) == [(0, 0), (1, 1)]


@pytest.mark.parametrize("threshold", [-0.1, 1.1, float("nan")])
def test_match_boxes_rejects_invalid_threshold(threshold: float) -> None:
    with pytest.raises(ValueError, match="threshold"):
        match_boxes([], [], threshold=threshold)
