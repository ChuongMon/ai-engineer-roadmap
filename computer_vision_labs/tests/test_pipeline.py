"""Unit tests for computer_vision_labs pipeline (pytest).

Chay: .venv\\Scripts\\python -m pytest tests/ -v
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from loader import ImageData, load_image, save_image
from preprocessing import (
    denoise,
    edge_detect,
    preprocess_pipeline,
    threshold,
    to_grayscale,
)
from roi import crop_roi, order_points, perspective_transform


@pytest.fixture
def sample_image(tmp_path: Path) -> np.ndarray:
    """Tao anh mau co cac vung mau phan biet."""
    img = np.zeros((300, 400, 3), dtype=np.uint8)
    img[50:150, 100:200] = (0, 0, 255)   # vung do
    img[150:250, 200:300] = (0, 255, 0)  # vung xanh luc
    img[200:280, 50:150] = (255, 0, 0)   # vung xanh duong
    p = tmp_path / "sample.png"
    cv2.imwrite(str(p), img)
    return img


def test_load_image_returns_imagedata(sample_image: np.ndarray, tmp_path: Path) -> None:
    """load_image phai tra ve ImageData co dung thuoc tinh."""
    p = tmp_path / "loaded.png"
    cv2.imwrite(str(p), sample_image)
    data = load_image(p)
    assert isinstance(data, ImageData)
    assert data.width == sample_image.shape[1]
    assert data.height == sample_image.shape[0]
    assert data.channels == 3
    assert data.dtype == "uint8"
    assert data.array.shape == sample_image.shape


def test_load_image_nonexistent_file_raises() -> None:
    """File khong ton tai phai raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_image(Path("duong/dan/khong/ton/tai/abc123.png"))


def test_to_grayscale(sample_image: np.ndarray) -> None:
    """to_grayscale phai giam ve 2 chieu va dung kieu du lieu."""
    gray = to_grayscale(sample_image)
    assert gray.ndim == 2
    assert gray.shape == sample_image.shape[:2]
    assert gray.dtype == np.uint8


def test_denoise(sample_image: np.ndarray) -> None:
    """denoise phai giu nguyen shape va kieu du lieu."""
    gray = to_grayscale(sample_image)
    blurred = denoise(gray, kernel_size=5)
    assert blurred.shape == gray.shape
    assert blurred.dtype == np.uint8


def test_threshold_returns_binary(sample_image: np.ndarray) -> None:
    """threshold phai tra ve anh nhi phan (chi co 0 va 255)."""
    gray = to_grayscale(sample_image)
    ret, binary = threshold(gray)
    assert binary.shape == gray.shape
    assert binary.dtype == np.uint8
    assert set(np.unique(binary)).issubset({0, 255})


def test_edge_detect(sample_image: np.ndarray) -> None:
    """edge_detect phai tra ve anh canh co dung shape."""
    gray = to_grayscale(sample_image)
    edges = edge_detect(gray)
    assert edges.shape == gray.shape
    assert edges.dtype == np.uint8


def test_preprocess_pipeline_returns_all_steps(sample_image: np.ndarray) -> None:
    """preprocess_pipeline phai tra ve tat ca 5 buoc: original, grayscale, denoised, threshold, edges."""
    result = preprocess_pipeline(sample_image)
    expected_keys = {"original", "grayscale", "denoised", "threshold", "edges"}
    assert set(result.keys()) == expected_keys
    assert result["original"].shape == sample_image.shape
    assert result["grayscale"].ndim == 2
    assert result["denoised"].ndim == 2
    assert result["threshold"].ndim == 2
    assert result["edges"].ndim == 2


def test_crop_roi(sample_image: np.ndarray) -> None:
    """crop_roi phai cat dung vung boi bounding box."""
    roi = crop_roi(sample_image, (100, 50, 200, 150))
    assert roi.shape == (100, 100, 3)


def test_order_points(sample_image: np.ndarray) -> None:
    """order_points phai sap xep 4 diem dung thu tu."""
    pts = np.array(
        [[50, 100], [200, 50], [180, 200], [80, 150]],
        dtype=np.float32,
    )
    rect = order_points(pts)
    assert rect.shape == (4, 2)
    # Diem trai-tren phai co tong x+y nho nhat
    assert rect[0][0] < rect[2][0]  # trai-tren x < phai-duoi x
    assert rect[0][1] < rect[2][1]  # trai-tren y < phai-duoi y


def test_perspective_transform(sample_image: np.ndarray, tmp_path: Path) -> None:
    """perspective_transform phai tra ve anh hinh chu nhat thang."""
    pts = np.array(
        [[50, 50], [350, 60], [330, 250], [70, 240]],
        dtype=np.float32,
    )
    warped = perspective_transform(sample_image, pts)
    assert warped.ndim == 3
    assert warped.shape[2] == 3
    assert warped.shape[0] > 50
    assert warped.shape[1] > 50


def test_save_image_creates_file(sample_image: np.ndarray, tmp_path: Path) -> None:
    """save_image phai tao file va file duoc doc lai dung."""
    out = tmp_path / "subdir" / "output.png"
    saved = save_image(sample_image, out)
    assert saved.exists()
    reloaded = cv2.imread(str(saved))
    assert reloaded is not None
    assert reloaded.shape == sample_image.shape
