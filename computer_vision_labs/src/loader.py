"""Loader module - doc anh thanh NumPy array."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np


@dataclass
class ImageData:
    """Container cho anh va metadata."""

    array: np.ndarray
    path: Path
    width: int
    height: int
    channels: int
    dtype: str


def load_image(path: str | Path) -> ImageData:
    """Doc anh tu file thanh NumPy array.

    Args:
        path: Duong den file anh.

    Returns:
        ImageData chua array va metadata.

    Raises:
        FileNotFoundError: Neu file khong ton tai.
        ValueError: Neu khong the doc anh.
    """
    image_path = Path(path)
    if not image_path.exists():
        raise FileNotFoundError(f"File anh khong ton tai: {image_path}")

    array = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if array is None:
        raise ValueError(f"Khong the doc anh: {image_path}")

    height, width, channels = array.shape
    return ImageData(
        array=array,
        path=image_path,
        width=width,
        height=height,
        channels=channels,
        dtype=str(array.dtype),
    )


def save_image(array: np.ndarray, output_path: str | Path) -> Path:
    """Luu NumPy array ra file anh.

    Args:
        array: Anh can luu.
        output_path: Duong dan file xuat.

    Returns:
        Duong dan file da luu.

    Raises:
        ValueError: Neu cv2.imwrite that bai.
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    success = cv2.imwrite(str(out_path), array)
    if not success:
        raise ValueError(f"Khong the ghi file anh: {out_path}")
    return out_path
