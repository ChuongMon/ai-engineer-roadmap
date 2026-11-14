"""ROI module - cat vung quan trong va chinh perspective."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def validate_quadrilateral(pts: np.ndarray, img_shape: tuple[int, int]) -> None:
    """Kiem tra 4 diem goc co hop le cho perspective transform.

    Kiem tra:
    - Dung 4 diem khac nhau.
    - Khong co diem trùng nhau.
    - Toa do nam trong khoang anh (0 <= x < w, 0 <= y < h).
    - Dien tich tui giac lon hon 0 (khong deu thang / khong bo goc).
    """
    if pts.shape != (4, 2):
        raise ValueError(f"Can dung dung 4 diem (4,2), nhan duoc {pts.shape}")

    h, w = img_shape[:2]

    for i, (x, y) in enumerate(pts):
        if not (0 <= x < w and 0 <= y < h):
            raise ValueError(f"Diem {i} ({x},{y}) nam ngoai anh (w={w}, h={h})")

    unique_pts = np.unique(pts, axis=0)
    if unique_pts.shape[0] < 4:
        raise ValueError(f"Co {4 - unique_pts.shape[0]} diem trung nhau, can 4 diem khac nhau")

    x = pts[:, 0]
    y = pts[:, 1]
    area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    if area < 1.0:
        raise ValueError(f"Dien tich tui giac qua nho ({area:.2f}), diem deu thang hoac bo goc")


def crop_roi(
    image: np.ndarray,
    bbox: tuple[int, int, int, int],
) -> np.ndarray:
    """Cat vung ROI tu bounding box.

    Args:
        image: Anh dau vao.
        bbox: (x_min, y_min, x_max, y_max).

    Returns:
        Anh da cat ROI.

    Raises:
        ValueError: Neu ROI rong sau khi cat.
    """
    x_min, y_min, x_max, y_max = bbox
    h, w = image.shape[:2]

    x_min = max(0, x_min)
    y_min = max(0, y_min)
    x_max = min(w, x_max)
    y_max = min(h, y_max)

    if x_max <= x_min or y_max <= y_min:
        raise ValueError("ROI rong sau khi cat (x_max <= x_min hoac y_max <= y_min)")

    return image[y_min:y_max, x_min:x_max].copy()


def order_points(pts: np.ndarray) -> np.ndarray:
    """Sap xep 4 diem theo thu tu: trai-tren, phai-tren, phai-duoi, trai-duoi."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def perspective_transform(
    image: np.ndarray,
    pts: np.ndarray,
    output_width: int | None = None,
    output_height: int | None = None,
) -> np.ndarray:
    """Bien doi perspective chinh anh bi nghiêng ve thang binh.

    Args:
        image: Anh dau vao.
        pts: Mang 4 diem (4, 2) tai cac goc vung can chinh.
        output_width: Chieu rong muon ra (neu None se tu dong tinh).
        output_height: Chieu cao muon ra (neu None se tu dong tinh).

    Returns:
        Anh da chinh perspective.

    Raises:
        ValueError: Neu 4 diem khong hop le.
    """
    validate_quadrilateral(pts, image.shape)
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    if output_width is None or output_height is None:
        width_a = np.linalg.norm(br - bl)
        width_b = np.linalg.norm(tr - tl)
        output_width = int(max(width_a, width_b))

        height_a = np.linalg.norm(tr - br)
        height_b = np.linalg.norm(tl - bl)
        output_height = int(max(height_a, height_b))

    if output_width < 10 or output_height < 10:
        raise ValueError(
            f"Kich thuc ket qua qua nho: {output_width}x{output_height}"
        )

    dst = np.array(
        [
            [0, 0],
            [output_width - 1, 0],
            [output_width - 1, output_height - 1],
            [0, output_height - 1],
        ],
        dtype=np.float32,
    )

    m = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, m, (output_width, output_height))


def crop_and_perspective(
    image: np.ndarray,
    pts: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Cat ROI va chinh perspective, tra ve (roi_crop, perspective_corrected)."""
    x_min = int(pts[:, 0].min())
    y_min = int(pts[:, 1].min())
    x_max = int(pts[:, 0].max())
    y_max = int(pts[:, 1].max())

    roi = crop_roi(image, (x_min, y_min, x_max, y_max))
    corrected = perspective_transform(image, pts)
    return roi, corrected
