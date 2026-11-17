"""Task 4.2 - Unit tests for OpenCV Preprocessing (pytest).

Chay: .venv\\Scripts\\python -m pytest tests/test_task42.py -v
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from day4_task42 import load_image, main, preprocessing_pipeline


@pytest.fixture
def sample_image(tmp_path: Path) -> np.ndarray:
    p = tmp_path / "sample.png"
    img = np.zeros((200, 300, 3), dtype=np.uint8)
    img[50:150, 100:200] = (0, 0, 255)
    cv2.imwrite(str(p), img)
    return img


def test_grayscale_conversion(sample_image: np.ndarray) -> None:
    gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
    assert gray.ndim == 2
    assert gray.shape == sample_image.shape[:2]
    assert gray.dtype == np.uint8


def test_gaussian_blur(sample_image: np.ndarray) -> None:
    gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    assert blurred.shape == gray.shape
    assert blurred.dtype == np.uint8


def test_threshold_binary(sample_image: np.ndarray) -> None:
    gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    assert thresh.shape == gray.shape
    assert thresh.dtype == np.uint8
    assert set(np.unique(thresh)).issubset({0, 255})


def test_threshold_otsu(sample_image: np.ndarray) -> None:
    gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    assert thresh.shape == gray.shape
    assert set(np.unique(thresh)).issubset({0, 255})


def test_adaptive_threshold(sample_image: np.ndarray) -> None:
    gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
    )
    assert adaptive.shape == gray.shape
    assert adaptive.dtype == np.uint8


def test_canny_edge_detection(sample_image: np.ndarray) -> None:
    gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    assert edges.shape == gray.shape
    assert edges.dtype == np.uint8


def test_morphology_on_canny(sample_image: np.ndarray) -> None:
    """Morphology (erosion/dilation/opening/closing) tren Canny edge map."""
    gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    kernel = np.ones((3, 3), np.uint8)
    eroded = cv2.erode(edges, kernel, iterations=1)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    opened = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    for op in (eroded, dilated, opened, closed):
        assert op.shape == edges.shape
        assert op.dtype == np.uint8


def test_morphology_on_binary(sample_image: np.ndarray) -> None:
    """Morphology (erosion/dilation/opening/closing) tren binary threshold image."""
    gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    eroded = cv2.erode(thresh, kernel, iterations=1)
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    for op in (eroded, dilated, opened, closed):
        assert op.shape == thresh.shape
        assert op.dtype == np.uint8


def test_blur_before_threshold(sample_image: np.ndarray) -> None:
    """Blur truoc threshold co the thay doi ket qua nhi phan."""
    gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh_gray = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    _, thresh_blur = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
    # Hai anh nhi phan phai co cung shape
    assert thresh_gray.shape == thresh_blur.shape
    assert thresh_gray.dtype == np.uint8
    assert thresh_blur.dtype == np.uint8


def test_preprocessing_pipeline_creates_outputs(
    sample_image: np.ndarray, tmp_path: Path
) -> None:
    """Pipeline xuat it thap 3 file tren cung mot anh, bao gom morphology tren binary."""
    out_dir = tmp_path / "outputs"
    outputs = preprocessing_pipeline(sample_image, out_dir)
    # Yeu cau bai tap: it thap 3 phuong phap tren cung mot anh
    assert len(outputs) >= 3
    assert "grayscale" in outputs
    assert "canny_gray" in outputs
    assert "opening_binary" in outputs
    assert "closing_binary" in outputs
    assert "compare_binary_morphology" in outputs
    for name, p in outputs.items():
        assert p.exists(), f"File thieu: {name} -> {p}"
        img = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
        assert img is not None, f"Khong doc lai duoc: {p}"
        assert img.size > 0


def test_main_processes_image_from_selected_folder(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    image_path = tmp_path / "label.png"
    cv2.imwrite(str(image_path), np.zeros((200, 300, 3), dtype=np.uint8))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "day4_task42.select_first_image_from_folder",
        lambda title: image_path,
    )

    assert main([]) == 0
    assert (tmp_path / "outputs/task42/task42_grayscale.png").is_file()
