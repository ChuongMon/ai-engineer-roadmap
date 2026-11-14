"""Task 4.3 - ROI & Perspective Transformation.

Quan trọng cho OCR cong nghiep:
  - Crop vung thong tin tu bounding box.
  - Perspective transform: chinh vung nhan bi nghiêng.
  - So sanh OCR input truoc va sau preprocessing.

Chay: python day4_task43.py [duong_dan_anh]
Neu khong co anh dau vao, chuong trinh tao anh mau co nhan bi nghiêng de minh hoa.
"""

from __future__ import annotations

import builtins
import sys
from pathlib import Path

import cv2
import numpy as np


def safe_print(text: str) -> None:
    """In ra CLI, tro ung loi ma hoa Windows cp1252."""
    try:
        builtins.print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8", errors="replace") + b"\n")


def create_synthetic_label(path: Path) -> np.ndarray:
    """Tao anh mau co mot hinh chu nhat bi nghiêng (mo phong nhan san pham).

    Tra ve anh goc va toa do 4 dinh cua vung nhan (goc trai tren, goc phai tren,
    goc phai duoi, goc trai duoi) theo thu tu can thiet cho perspective transform.
    """
    img = np.zeros((500, 700, 3), dtype=np.uint8)
    img[0:500, 0:700] = (240, 240, 240)  # nen xam nhat

    # Ve mot hinh chu nhat bi nghiêng (mo phong nhan dan ong)
    # 4 dinh: (x, y)
    pts = np.array(
        [[180, 120], [520, 150], [480, 320], [140, 300]], dtype=np.float32
    )
    pts_int = pts.astype(np.int32)
    cv2.fillConvexPoly(img, pts_int, (255, 255, 255))

    # Ve chu "LABEL" o trong vung nhan (mo phong text)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Dat text o tam cua vung nhan (khoang tam cua 4 dinh)
    cx = int(pts[:, 0].mean())
    cy = int(pts[:, 1].mean())
    cv2.putText(img, "LABEL", (cx - 60, cy + 10), font, 1.4, (0, 0, 0), 3, cv2.LINE_AA)

    # Ve duong vien den xung quanh de de nhan dinh
    cv2.polylines(img, [pts_int], isClosed=True, color=(0, 0, 0), thickness=2)

    cv2.imwrite(str(path), img)
    safe_print(f"[INFO] Da tao anh mau nhan bi nghiêng: {path}")
    return img, pts


def load_image(path: Path | None = None) -> tuple[np.ndarray, np.ndarray | None]:
    """Doc anh. Neu khong co, tao anh mau va tra ve toa do 4 dinh nhan."""
    if path is None:
        path = Path("task43_synthetic.png")
    if not path.exists():
        img, pts = create_synthetic_label(path)
        return img, pts
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Khong the doc anh: {path}")
    return img, None


def crop_roi(img: np.ndarray, pts: np.ndarray, out_dir: Path) -> tuple[np.ndarray, Path]:
    """Crop vung bounding box chua 4 dinh nhan."""
    x_min = int(pts[:, 0].min())
    y_min = int(pts[:, 1].min())
    x_max = int(pts[:, 0].max())
    y_max = int(pts[:, 1].max())

    # Bo khong qua anh
    h, w = img.shape[:2]
    x_min = max(0, x_min)
    y_min = max(0, y_min)
    x_max = min(w, x_max)
    y_max = min(h, y_max)

    roi = img[y_min:y_max, x_min:x_max].copy()
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "task43_roi_crop.png"
    cv2.imwrite(str(p), roi)
    safe_print(f"[OK] Crop ROI: {p}  shape={roi.shape}")
    return roi, p


def perspective_correct(img: np.ndarray, pts: np.ndarray, out_dir: Path) -> tuple[np.ndarray, Path]:
    """Chinh vung nhan bi nghiêng bang perspective transform.

    Map 4 dinh nhan (nghiêng) ve mot hinh chu nhat thang binh thuong.
    """
    # Thu tuc sap xep 4 dinh theo thu tu: trai-tren, phai-tren, phai-duoi, trai-duoi
    # pts dau vao da duoc sap xep theo thu luon trong create_synthetic_label,
    # nhung de an toan ta sap xep lai lai.
    rect = np.zeros((4, 2), dtype=np.float32)

    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]    # trai-tren (x min + y min)
    rect[2] = pts[np.argmax(s)]    # phai-duoi (x max + y max)
    rect[1] = pts[np.argmin(diff)] # phai-tren (x max - y min nho nhat)
    rect[3] = pts[np.argmax(diff)] # trai-duoi

    # Tinh chieu dai / chieu rong cua hinh chu nhat dich
    (tl, tr, br, bl) = rect
    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = int(max(width_a, width_b))

    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = int(max(height_a, height_b))

    # Dinh dinh dich (hinh chu nhat thang)
    dst = np.array(
        [[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]],
        dtype=np.float32,
    )

    # Ma tran bien doi perspective
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (max_width, max_height))

    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "task43_perspective_corrected.png"
    cv2.imwrite(str(p), warped)
    safe_print(f"[OK] Perspective-corrected: {p}  shape={warped.shape}")
    return warped, p


def side_by_side(original: np.ndarray, corrected: np.ndarray, out_dir: Path) -> Path:
    """Ghep 2 anh ben nhau de so sanh truoc/sau."""
    h1, w1 = original.shape[:2]
    h2, w2 = corrected.shape[:2]
    h = max(h1, h2)
    canvas = np.zeros((h, w1 + w2, 3), dtype=np.uint8)
    canvas[0:h1, 0:w1] = original
    canvas[0:h2, w1 : w1 + w2] = corrected

    # Chu thich
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, "Truoc (nghiêng)", (10, 30), font, 0.8, (0, 0, 255), 2)
    cv2.putText(canvas, "Sau (da chinh)", (w1 + 10, 30), font, 0.8, (0, 255, 0), 2)

    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "task43_before_after.png"
    cv2.imwrite(str(p), canvas)
    safe_print(f"[OK] So sanh truoc/sau: {p}  shape={canvas.shape}")
    return p


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    out_dir = Path("outputs/task43")

    img, pts = load_image(path)

    if pts is None:
        # Neu anh dau vao khong co toa do, tao anh mau de minh hoa
        img, pts = create_synthetic_label(Path("task43_synthetic.png"))

    safe_print(f"\nAnh goc: {img.shape}, dtype={img.dtype}")
    safe_print(f"Toa do 4 dinh nhan:\n{pts}")

    # 1. Crop ROI
    roi, roi_path = crop_roi(img, pts, out_dir)

    # 2. Perspective correct (dung toa do 4 dinh tren anh goc)
    corrected, corrected_path = perspective_correct(img, pts, out_dir)

    # 3. Ghep truoc/sau
    cmp_path = side_by_side(img, corrected, out_dir)

    safe_print(f"\n[HOAN TAT] Tat ca file ket qua duoc luu o: {out_dir.resolve()}")
    safe_print(f"  - ROI crop:        {roi_path.name}")
    safe_print(f"  - Perspective:     {corrected_path.name}")
    safe_print(f"  - Before/After:    {cmp_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
