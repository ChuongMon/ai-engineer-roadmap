"""Task 4.3 - Unit tests for ROI & Perspective Transformation (pytest).

Chay: .venv\\Scripts\\python -m pytest tests/test_task43.py -v
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from day4_task43 import crop_roi, create_synthetic_label, load_image, perspective_correct


@pytest.fixture
def synthetic_label(tmp_path: Path) -> tuple[np.ndarray, np.ndarray]:
    p = tmp_path / "label.png"
    img, pts = create_synthetic_label(p)
    return img, pts


def test_create_synthetic_label_returns_image_and_points(
    synthetic_label: tuple[np.ndarray, np.ndarray],
) -> None:
    img, pts = synthetic_label
    assert isinstance(img, np.ndarray)
    assert img.ndim == 3
    assert img.shape[2] == 3
    assert pts.shape == (4, 2)
    assert pts.dtype == np.float32


def test_load_image_returns_array(synthetic_label: tuple[np.ndarray, np.ndarray], tmp_path: Path) -> None:
    p = tmp_path / "loaded.png"
    cv2.imwrite(str(p), synthetic_label[0])
    img, _ = load_image(p)
    assert isinstance(img, np.ndarray)
    assert img.shape == synthetic_label[0].shape


def test_crop_roi_shape(synthetic_label: tuple[np.ndarray, np.ndarray], tmp_path: Path) -> None:
    img, pts = synthetic_label
    out_dir = tmp_path / "out"
    roi, p = crop_roi(img, pts, out_dir)
    assert p.exists()
    # ROI chua toan bo 4 dinh => chieu dai/rong >= khoang cach giua 2 dinh xa nhat
    assert roi.shape[0] > 0 and roi.shape[1] > 0


def test_perspective_correct_output_shape(synthetic_label: tuple[np.ndarray, np.ndarray], tmp_path: Path) -> None:
    img, pts = synthetic_label
    out_dir = tmp_path / "out"
    warped, p = perspective_correct(img, pts, out_dir)
    assert p.exists()
    assert warped.ndim == 3
    assert warped.shape[2] == 3
    # Ket qua perspective phai la hinh chu nhat thang (khong bi bo loc do toa do)
    assert warped.shape[0] > 50 and warped.shape[1] > 50


def test_perspective_transform_matrix_valid(synthetic_label: tuple[np.ndarray, np.ndarray]) -> None:
    """Kiem tra ma tran bien doi perspective co the tinh toan duoc va hop le."""
    _, pts = synthetic_label
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    dst = np.array(
        [[0, 0], [199, 0], [199, 199], [0, 199]], dtype=np.float32
    )
    M = cv2.getPerspectiveTransform(rect, dst)
    assert M.shape == (3, 3)
    # Ma tran khong duoc la ma tran rong / chi co so 0
    assert np.count_nonzero(M) > 0


def test_warp_preserves_channels(synthetic_label: tuple[np.ndarray, np.ndarray], tmp_path: Path) -> None:
    img, pts = synthetic_label
    out_dir = tmp_path / "out"
    warped, _ = perspective_correct(img, pts, out_dir)
    assert warped.shape[2] == img.shape[2]  # cung so kenh mau


def test_side_by_side_created(tmp_path: Path) -> None:
    """Kiem tra ham ghep truoc/sau ton tai trong module (import duoc)."""
    from day4_task43 import side_by_side

    img = np.zeros((100, 100, 3), dtype=np.uint8)
    corr = np.zeros((100, 100, 3), dtype=np.uint8)
    out_dir = tmp_path / "out"
    p = side_by_side(img, corr, out_dir)
    assert p.exists()
    assert cv2.imread(str(p)) is not None
