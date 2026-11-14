"""Task 4.1 - Unit tests for NumPy Image Fundamentals (pytest).

Chay: .venv\\Scripts\\python -m pytest tests/test_task41.py -v
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from day4_task41 import create_synthetic_image, load_image


@pytest.fixture
def synthetic_image(tmp_path: Path) -> np.ndarray:
    p = tmp_path / "synthetic.png"
    return create_synthetic_image(p)


def test_read_image_returns_numpy_array(synthetic_image: np.ndarray) -> None:
    """Doc anh thanh NumPy array (khong phai None, la ndarray)."""
    assert isinstance(synthetic_image, np.ndarray)
    assert synthetic_image.size > 0


def test_image_shape_dtype_ndim(synthetic_image: np.ndarray) -> None:
    """shape co 3 thanh phan, dtype uint8, ndim bang 3."""
    h, w, c = synthetic_image.shape
    assert h > 0 and w > 0
    assert c == 3
    assert synthetic_image.dtype == np.uint8
    assert synthetic_image.ndim == 3


def test_access_pixel(synthetic_image: np.ndarray) -> None:
    """Truy cap pixel tra ve gia tri BGR 3 kenh."""
    px = synthetic_image[100, 100]
    assert px.shape == (3,)
    assert px.dtype == np.uint8
    # tai vi tri (100,100) nam trong vung xanh luc (0,255,0) [BGR]
    assert int(px[0]) == 0   # Blue
    assert int(px[1]) == 255 # Green
    assert int(px[2]) == 0   # Red


def test_access_roi(synthetic_image: np.ndarray) -> None:
    """Truy cap vung ROI co shape du kien."""
    roi = synthetic_image[50:200, 50:250]
    assert roi.shape == (150, 200, 3)
    # Vung xanh luc: kenh Green cao nhat
    means = roi.mean(axis=(0, 1))
    assert int(np.argmax(means)) == 1  # Green


def test_crop(synthetic_image: np.ndarray, tmp_path: Path) -> None:
    """Crop nua trai giam chieu rong."""
    crop = synthetic_image[:, : synthetic_image.shape[1] // 2]
    assert crop.shape[1] == synthetic_image.shape[1] // 2
    assert crop.shape[0] == synthetic_image.shape[0]


def test_resize(synthetic_image: np.ndarray) -> None:
    """Resize ve kich co 300x200."""
    resized = cv2.resize(synthetic_image, (300, 200), interpolation=cv2.INTER_AREA)
    assert resized.shape == (200, 300, 3)


def test_transpose(synthetic_image: np.ndarray) -> None:
    """Transpose dao hang va cot."""
    transposed = np.transpose(synthetic_image, (1, 0, 2))
    assert transposed.shape == (synthetic_image.shape[1], synthetic_image.shape[0], 3)


def test_convert_bgr_to_rgb(synthetic_image: np.ndarray) -> None:
    """Chuyen doi BGR -> RGB, shape khong thay doi, kenh duoc hoan doi."""
    rgb = cv2.cvtColor(synthetic_image, cv2.COLOR_BGR2RGB)
    assert rgb.shape == synthetic_image.shape
    # Pixel xanh luc (0,255,0) [BGR] -> (0,255,0) [RGB] cung vi Green o giua,
    # nhung kiem tra hoan doi chan Red/Blue voi pixel do (0,0,255) [BGR] -> (255,0,0) [RGB]
    red_bgr = synthetic_image[100, 450]  # nam trong vung do
    red_rgb = rgb[100, 450]
    assert int(red_bgr[0]) == int(red_rgb[2])  # B <-> R
    assert int(red_bgr[2]) == int(red_rgb[0])


def test_convert_bgr_to_gray(synthetic_image: np.ndarray) -> None:
    """Chuyen doi BGR -> Grayscale giam xuong 1 kenh."""
    gray = cv2.cvtColor(synthetic_image, cv2.COLOR_BGR2GRAY)
    assert gray.ndim == 2
    assert gray.shape == synthetic_image.shape[:2]
    assert gray.dtype == np.uint8


def test_synthetic_image_is_written_and_reloadable(tmp_path: Path) -> None:
    """Anh tao dong duoc luu va doc lai bang OpenCV."""
    p = tmp_path / "out.png"
    img = create_synthetic_image(p)
    assert p.exists()
    reloaded = cv2.imread(str(p), cv2.IMREAD_COLOR)
    assert reloaded is not None
    assert reloaded.shape == img.shape
