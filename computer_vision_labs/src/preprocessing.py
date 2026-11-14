"""Preprocessing module - cac phuong phap xu ly anh truoc."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def _validate_kernel_size(kernel_size: int) -> int:
    """Kiem tra kich thuc kernel: phai duong va le."""
    if kernel_size <= 0:
        raise ValueError(f"kernel_size phai duong, nhan duoc {kernel_size}")
    if kernel_size % 2 == 0:
        kernel_size += 1
    return kernel_size


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Chuyen anh BGR/BGRA sang Grayscale."""
    if len(image.shape) == 2:
        return image.copy()
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def denoise(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """Lam muot anh bang Gaussian blur de loai nhieu."""
    kernel_size = _validate_kernel_size(kernel_size)
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def threshold(
    image: np.ndarray,
    threshold_value: int = 127,
    max_value: int = 255,
    method: int = cv2.THRESH_BINARY + cv2.THRESH_OTSU,
) -> tuple[float, np.ndarray]:
    """Ap dung nhi phan hoa anh.

    Returns:
        (threshold_value_used, binary_image)
    """
    if len(image.shape) == 3:
        image = to_grayscale(image)
    ret, binary = cv2.threshold(image, threshold_value, max_value, method)
    return ret, binary


def edge_detect(
    image: np.ndarray,
    threshold1: int = 100,
    threshold2: int = 200,
) -> np.ndarray:
    """Phat hien canh bang Canny edge detection."""
    if len(image.shape) == 3:
        image = to_grayscale(image)
    return cv2.Canny(image, threshold1, threshold2)


def preprocess_pipeline(
    image: np.ndarray,
) -> dict[str, np.ndarray]:
    """Chay toan bo pipeline preprocessing tra ve dict tat ca buoc."""
    gray = to_grayscale(image)
    denoised = denoise(gray, kernel_size=5)
    _, binary = threshold(denoised)
    edges = edge_detect(denoised)

    return {
        "original": image,
        "grayscale": gray,
        "denoised": denoised,
        "threshold": binary,
        "edges": edges,
    }
