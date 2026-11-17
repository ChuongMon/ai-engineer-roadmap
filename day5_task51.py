"""Task 5.1 - Contours và bounding boxes.

Tìm contour trên ảnh nhị phân, lọc theo diện tích,
tính boundingRect (hình chữ nhật thẳng theo trục) và minAreaRect
(hình chữ nhật nhỏ nhất, có thể xoay), vẽ minh họa và lưu ảnh kết quả.

Chạy: python day5_task51.py
Không cần ảnh đầu vào: tự tạo ảnh tổng hợp 5 hình chữ nhật
(ít nhất một hình xoay, một vùng nhiễu nhỏ).
"""

from __future__ import annotations

import builtins
import sys
from math import isfinite
from numbers import Real
from pathlib import Path

import cv2
import numpy as np


def safe_print(text: str) -> None:
    """In ra CLI, tro ung loi ma hoa Windows cp1252."""
    try:
        builtins.print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8", errors="replace") + b"\n")


def validate_binary_image(img: np.ndarray) -> None:
    """Kiểm tra ảnh đầu vào là ảnh nhị phân 2D uint8 (chỉ giá trị 0 và 255).

    Ảnh nhị phân cũng là grayscale (2 chiều), nên ndim == 2 là yêu cầu.
    Ảnh toàn đen hợp lệ nhưng sẽ không có contour nào.
    """
    if not isinstance(img, np.ndarray):
        raise TypeError(f"Anh phai la numpy.ndarray, nhan {type(img).__name__}")
    if img.ndim != 2:
        raise ValueError(f"Anh nhi phan phai la 2 chieu (grayscale), nhan ndim={img.ndim}")
    if img.dtype != np.uint8:
        raise ValueError(f"Anh nhi phan phai co dtype uint8, nhan {img.dtype}")
    unique = np.unique(img)
    if not np.all(np.isin(unique, [0, 255])):
        raise ValueError("Anh nhi phan chi duoc chua gia tri 0 va 255")


def find_contours(binary_img: np.ndarray) -> list[np.ndarray]:
    """Tim contour ngoai tren anh nhi phan.

    Tra ve danh sach rong neu khong co contour (vi du anh toan den).
    Dung RETR_EXTERNAL chi lay contour ngoai; CHAIN_APPROX_SIMPLE bo diem du.
    """
    validate_binary_image(binary_img)
    contours, _ = cv2.findContours(
        binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    return list(contours)


def filter_contours_by_area(
    contours: list[np.ndarray], min_area: float, max_area: float
) -> list[np.ndarray]:
    """Loc contour theo dien tich (cv2.contourArea).

    Yeu cau cac nguong huu han, min_area >= 0 va min_area <= max_area.
    Dien tich contour tinh tu da giac cac diem tra ve, khong phai so pixel trang.
    """
    if not isinstance(min_area, Real) or not isinstance(max_area, Real):
        raise ValueError("min_area va max_area phai la so huu han")
    try:
        min_area = float(min_area)
        max_area = float(max_area)
    except OverflowError as exc:
        raise ValueError("min_area va max_area phai la so huu han") from exc
    if not isfinite(min_area) or not isfinite(max_area):
        raise ValueError("min_area va max_area phai la so huu han")
    if min_area < 0:
        raise ValueError(f"min_area khong duoc am: {min_area}")
    if min_area > max_area:
        raise ValueError(
            f"min_area ({min_area}) khong duoc lon hon max_area ({max_area})"
        )
    return [
        c
        for c in contours
        if min_area <= cv2.contourArea(c) <= max_area
    ]


def bounding_boxes(contours: list[np.ndarray]) -> list[tuple[int, int, int, int]]:
    """Tinh boundingRect (x, y, w, h) cho moi contour.

    Hinh chu nhat thang theo truc anh. Neu vat the nghiêng, box se du thua.
    """
    return [cv2.boundingRect(c) for c in contours]


def min_area_rects(contours: list[np.ndarray]) -> list[tuple]:
    """Tinh minAreaRect cho moi contour.

    Tra ve danh sach tuple ((center_x, center_y), (width, height), angle).
    Hinh chu nhat nho nhat bao contour, co the xoay — deu ích khi vat the xoay
    trong mat phinh, KHONG phai chinh sua pho canh (mat thang thanh thang).
    """
    return [cv2.minAreaRect(c) for c in contours]


def rect_box_points(rects: list[tuple]) -> list[np.ndarray]:
    """Lay 4 dinh (float32, shape (4,2)) cua moi minAreaRect.

    Thu tu 4 dinh khong co dinh. Can order_points neu muon thu tu lap dan.
    """
    return [cv2.boxPoints(r) for r in rects]


def draw_results(
    img: np.ndarray,
    contours: list[np.ndarray],
    boxes: list[tuple[int, int, int, int]],
    rotated_points: list[np.ndarray],
) -> np.ndarray:
    """Ve contour (xanh la), boundingRect (xanh duong), minAreaRect (do) len anh."""
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(vis, contours, -1, (0, 255, 0), 2)
    for x, y, w, h in boxes:
        cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 0, 0), 2)
    for pts in rotated_points:
        pts_int = np.int32(pts)
        cv2.polylines(vis, [pts_int], isClosed=True, color=(0, 0, 255), thickness=2)
    return vis


def create_synthetic_image(path: Path) -> np.ndarray:
    """Tao anh nhi phan 5 hinh chu nhat (1 xoay, 1 nhieu nho)."""
    img = np.zeros((400, 500), dtype=np.uint8)

    # Hinh chu nhat thang (toa do/kich thuct biet truoc)
    cv2.rectangle(img, (50, 50), (150, 110), 255, -1)      # 100x60 tai (50,50)
    cv2.rectangle(img, (200, 80), (280, 120), 255, -1)     # 80x40
    cv2.rectangle(img, (340, 60), (430, 110), 255, -1)     # 90x50

    # Hinh chu nhat xoay (tam 250,200, kich thuoc 120x70, xoay 30 do)
    rect = ((250, 200), (120, 70), 30)
    box = cv2.boxPoints(rect)
    cv2.fillConvexPoly(img, np.int32(box), 255)

    # Vung nhieu nho (10x10 = 100 px)
    cv2.rectangle(img, (100, 300), (110, 310), 255, -1)

    cv2.imwrite(str(path), img)
    safe_print(f"[INFO] Da tao anh tong hop: {path}")
    return img


def main() -> int:
    out_dir = Path("outputs/task51")
    out_dir.mkdir(parents=True, exist_ok=True)

    synth_path = Path("task51_synthetic.png")
    img = create_synthetic_image(synth_path)

    contours = find_contours(img)
    safe_print(f"\n[CONTOUR] So contour tim thay: {len(contours)}")

    min_area, max_area = 150.0, 100000.0
    filtered = filter_contours_by_area(contours, min_area, max_area)
    safe_print(
        f"[FILTER] Sau loc dien tich [{min_area}, {max_area}]: {len(filtered)}"
    )

    boxes = bounding_boxes(filtered)
    rects = min_area_rects(filtered)
    rotated_points = rect_box_points(rects)

    vis = draw_results(img, filtered, boxes, rotated_points)
    out_path = out_dir / "task51_contours_boxes.png"
    cv2.imwrite(str(out_path), vis)
    safe_print(f"\n[OK] Luu anh minh hoa: {out_path}")

    for i, (box, rect) in enumerate(zip(boxes, rects)):
        x, y, w, h = box
        (cx, cy), (rw, rh), angle = rect
        safe_print(
            f"  Hinh {i+1}: boundingRect=({x},{y},{w},{h}), "
            f"minAreaRect=center=({cx:.1f},{cy:.1f}) size=({rw:.1f},{rh:.1f}) angle={angle:.1f}"
        )

    safe_print(f"\n[HOAN TAT] Output tai: {out_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
