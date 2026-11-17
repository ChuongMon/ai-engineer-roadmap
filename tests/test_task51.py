"""Task 5.1 - Unit tests for contours and bounding boxes (pytest).

Chạy: .venv\\Scripts\\python -m pytest tests/test_task51.py -v
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from day5_task51 import (
    bounding_boxes,
    create_synthetic_image,
    filter_contours_by_area,
    find_contours,
    min_area_rects,
    rect_box_points,
    validate_binary_image,
)


@pytest.fixture
def binary_rectangle() -> np.ndarray:
    """Ảnh nhị phân có một hình chữ nhật trắng 100x60 tại (50,50) trên nền đen."""
    img = np.zeros((200, 200), dtype=np.uint8)
    img[50:110, 50:150] = 255
    return img


@pytest.fixture
def binary_with_noise() -> np.ndarray:
    """Ảnh nhị phân có hình chữ nhật lớn và vùng nhiễu nhỏ."""
    img = np.zeros((200, 200), dtype=np.uint8)
    img[50:110, 50:150] = 255      # lớn (diện tích ~6000)
    img[150:160, 150:170] = 255     # nhỏ (diện tích ~100)
    return img


def test_validate_binary_image_accepts_valid(binary_rectangle: np.ndarray) -> None:
    validate_binary_image(binary_rectangle)


def test_validate_binary_image_accepts_all_black() -> None:
    """Ảnh toàn đen là nhị phân hợp lệ (không có contour)."""
    img = np.zeros((100, 100), dtype=np.uint8)
    validate_binary_image(img)


def test_validate_binary_image_rejects_3d() -> None:
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    with pytest.raises(ValueError):
        validate_binary_image(img)


def test_validate_binary_image_rejects_non_uint8() -> None:
    img = np.zeros((100, 100), dtype=np.float32)
    with pytest.raises(ValueError):
        validate_binary_image(img)


def test_validate_binary_image_rejects_intermediate_values() -> None:
    """Grayscale có giá trị trung gian (127) không phải ảnh nhị phân."""
    img = np.full((100, 100), 127, dtype=np.uint8)
    with pytest.raises(ValueError):
        validate_binary_image(img)


def test_find_contours_returns_empty_for_black_image() -> None:
    img = np.zeros((100, 100), dtype=np.uint8)
    contours = find_contours(img)
    assert contours == []


def test_find_contours_finds_one_rectangle(binary_rectangle: np.ndarray) -> None:
    contours = find_contours(binary_rectangle)
    assert len(contours) == 1


def test_filter_removes_small_noise(binary_with_noise: np.ndarray) -> None:
    contours = find_contours(binary_with_noise)
    assert len(contours) == 2
    filtered = filter_contours_by_area(contours, min_area=200, max_area=100000)
    assert len(filtered) == 1


def test_filter_keeps_all_when_range_wide(binary_with_noise: np.ndarray) -> None:
    contours = find_contours(binary_with_noise)
    filtered = filter_contours_by_area(contours, min_area=0, max_area=1000000)
    assert len(filtered) == 2


def test_filter_rejects_negative_min_area() -> None:
    with pytest.raises(ValueError):
        filter_contours_by_area([], min_area=-1, max_area=100)


def test_filter_rejects_min_greater_than_max() -> None:
    with pytest.raises(ValueError):
        filter_contours_by_area([], min_area=200, max_area=100)


def test_bounding_rect_matches_known_rectangle(binary_rectangle: np.ndarray) -> None:
    contours = find_contours(binary_rectangle)
    boxes = bounding_boxes(contours)
    assert len(boxes) == 1
    x, y, w, h = boxes[0]
    assert x == 50 and y == 50
    assert w == 100 and h == 60


def test_min_area_rect_rotated_has_angle() -> None:
    """Hình chữ nhật xoay phải cho minAreaRect có góc khác 0."""
    img = np.zeros((200, 200), dtype=np.uint8)
    rect = ((100, 100), (80, 40), 30.0)
    box = cv2.boxPoints(rect)
    cv2.fillConvexPoly(img, np.int32(box), 255)

    contours = find_contours(img)
    assert len(contours) == 1
    rects = min_area_rects(contours)
    (cx, cy), (rw, rh), angle = rects[0]
    assert abs(angle) > 1.0


def test_rect_box_points_returns_four_points() -> None:
    img = np.zeros((200, 200), dtype=np.uint8)
    img[50:110, 50:150] = 255
    contours = find_contours(img)
    rects = min_area_rects(contours)
    points = rect_box_points(rects)
    assert len(points) == 1
    assert points[0].shape == (4, 2)
    assert points[0].dtype == np.float32


def test_rect_box_points_enclose_rectangle() -> None:
    """4 đỉnh minAreaRect phải bao lấy hình chữ nhật mẫu (trong sai số)."""
    img = np.zeros((200, 200), dtype=np.uint8)
    img[50:110, 50:150] = 255  # hình 100x60 tại (50,50)
    contours = find_contours(img)
    rects = min_area_rects(contours)
    points = rect_box_points(rects)[0]
    xs = points[:, 0]
    ys = points[:, 1]
    assert xs.min() <= 50 + 2
    assert xs.max() >= 150 - 2
    assert ys.min() <= 50 + 2
    assert ys.max() >= 110 - 2


def test_create_synthetic_image_creates_file(tmp_path: Path) -> None:
    p = tmp_path / "synth.png"
    img = create_synthetic_image(p)
    assert p.exists()
    assert img.ndim == 2
    assert img.dtype == np.uint8


def test_synthetic_image_finds_five_contours(tmp_path: Path) -> None:
    p = tmp_path / "synth.png"
    img = create_synthetic_image(p)
    contours = find_contours(img)
    assert len(contours) == 5
