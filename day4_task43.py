"""Task 4.3 - ROI & Perspective Transformation.

Quan trong cho OCR cong nghiep:
  - Cat vung thong tin tu bounding box.
  - Perspective transform: chinh vung nhan bi nghiêng.
  - So sanh OCR input truoc va sau preprocessing.

Chay: python day4_task43.py [duong_dan_anh] [x1,y1,x2,y2,x3,y3,x4,y4]
  - duong_dan_anh: anh dau vao (bat buoc neu khong co anh mau).
  - x1,y1,...,x4,y4: 4 toa do goc cua vung nhan (trai-tren, phai-tren,
    phai-duoi, trai-duoi). Neu khong co, chuong trinh se bao loi thay thay
    the bang anh synthetic.

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


def create_synthetic_label(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Tao anh mau co mot hinh chu nhat bi nghiêng (mo phong nhan san pham).

    Tra ve (anh, pts) voi pts la 4 toa do goc (trai-tren, phai-tren,
    phai-duoi, trai-duoi) kieu float32.
    """
    img = np.zeros((500, 700, 3), dtype=np.uint8)
    img[0:500, 0:700] = (240, 240, 240)  # nen xam nhat

    # 4 dinh cua hinh chu nhat bi nghiêng
    pts = np.array(
        [[180, 120], [520, 150], [480, 320], [140, 300]], dtype=np.float32
    )
    pts_int = pts.astype(np.int32)
    cv2.fillConvexPoly(img, pts_int, (255, 255, 255))

    font = cv2.FONT_HERSHEY_SIMPLEX
    cx = int(pts[:, 0].mean())
    cy = int(pts[:, 1].mean())
    cv2.putText(img, "LABEL", (cx - 60, cy + 10), font, 1.4, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.polylines(img, [pts_int], isClosed=True, color=(0, 0, 0), thickness=2)

    cv2.imwrite(str(path), img)
    safe_print(f"[INFO] Da tao anh mau nhan bi nghiêng: {path}")
    return img, pts


def load_image(path: Path | None = None) -> tuple[np.ndarray, np.ndarray | None]:
    """Doc anh bang OpenCV.

    Neu khong co duong dan hoac file khong ton tai -> tao anh mau va tra ve pts.
    Neu co duong dan hop le -> tra ve (anh, None) (nguoi dung phai cung cap pts qua CLI).
    """
    if path is None or not path.exists():
        img, pts = create_synthetic_label(Path("task43_synthetic.png"))
        return img, pts
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Khong the doc anh: {path}")
    return img, None


def parse_pts(pts_str: str | None, expected: int = 8) -> np.ndarray | None:
    """Chuyen chuoi "x1,y1,x2,y2,x3,y3,x4,y4" thanh mang (4,2) float32.

    Tra ve None neu pts_str la None.
    Ra ValueError neu so luong toa do khong dung.
    """
    if pts_str is None:
        return None
    coords = [int(v.strip()) for v in pts_str.split(",")]
    if len(coords) != expected:
        raise ValueError(
            f"Can dung {expected} toa do (x1,y1,...,x4,y4), nhan duoc {len(coords)}"
        )
    return np.array(
        [
            [coords[0], coords[1]],
            [coords[2], coords[3]],
            [coords[4], coords[5]],
            [coords[6], coords[7]],
        ],
        dtype=np.float32,
    )


def validate_quadrilateral(pts: np.ndarray, img_shape: tuple[int, int]) -> None:
    """Kiem tra 4 diem goc co hop lệ cho perspective transform.

    Kiem tra:
    - Dung 4 diem khac nhau.
    - Khong co diem trùng nhau.
    - Toa do nam trong khoang anh (0 <= x < w, 0 <= y < h).
    - Dien tich tui giac lon hon 0 (khong deu thang / khong bo goc).
    """
    if pts.shape != (4, 2):
        raise ValueError(f"Can dung dung 4 diem (4,2), nhan duoc {pts.shape}")

    h, w = img_shape[:2]

    # 1. Toa do nam trong anh
    for i, (x, y) in enumerate(pts):
        if not (0 <= x < w and 0 <= y < h):
            raise ValueError(
                f"Diem {i} ({x},{y}) nam ngoai anh (w={w}, h={h})"
            )

    # 2. Khong co diem trùng nhau
    unique_pts = np.unique(pts, axis=0)
    if unique_pts.shape[0] < 4:
        raise ValueError(f"Co {4 - unique_pts.shape[0]} diem trung nhau, can 4 diem khac nhau")

    # 3. Tinh dien tich tui giac (shoelace formula)
    x = pts[:, 0]
    y = pts[:, 1]
    area = 0.5 * np.abs(
        np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))
    )
    if area < 1.0:
        raise ValueError(f"Dien tich tui giac qua nho ({area:.2f}), diem deu thang hoac bo goc")


def order_points(pts: np.ndarray) -> np.ndarray:
    """Sap xep 4 diem theo thu tu: trai-tren, phai-tren, phai-duoi, trai-duoi."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]    # trai-tren
    rect[2] = pts[np.argmax(s)]    # phai-duoi
    rect[1] = pts[np.argmin(diff)] # phai-tren
    rect[3] = pts[np.argmax(diff)] # trai-duoi
    return rect


def crop_roi(img: np.ndarray, pts: np.ndarray, out_dir: Path) -> tuple[np.ndarray, Path]:
    """Cat vung bounding box chua 4 diem nhan."""
    x_min = int(pts[:, 0].min())
    y_min = int(pts[:, 1].min())
    x_max = int(pts[:, 0].max())
    y_max = int(pts[:, 1].max())

    h, w = img.shape[:2]
    x_min = max(0, x_min)
    y_min = max(0, y_min)
    x_max = min(w, x_max)
    y_max = min(h, y_max)

    if x_max <= x_min or y_max <= y_min:
        raise ValueError("ROI rong sau khi cat (x_max <= x_min hoac y_max <= y_min)")

    roi = img[y_min:y_max, x_min:x_max].copy()
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "task43_roi_crop.png"
    cv2.imwrite(str(p), roi)
    safe_print(f"[OK] Crop ROI: {p}  shape={roi.shape}")
    return roi, p


def perspective_correct(
    img: np.ndarray, pts: np.ndarray, out_dir: Path
) -> tuple[np.ndarray, Path]:
    """Chinh vung nhan bi nghiêng bang perspective transform."""
    validate_quadrilateral(pts, img.shape)

    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = int(max(width_a, width_b))

    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = int(max(height_a, height_b))

    if max_width < 10 or max_height < 10:
        raise ValueError(
            f"Kich thuc ket qua qua nho: {max_width}x{max_height}"
        )

    dst = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype=np.float32,
    )

    m = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, m, (max_width, max_height))

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
    pts_str = sys.argv[2] if len(sys.argv) > 2 else None
    out_dir = Path("outputs/task43")

    img, pts = load_image(path)

    # Neu nguoi dung khong cung cap pts qua CLI va anh khong co pts (load tu file thuc),
    # thi bao loi thay the thay the anh goc bang anh synthetic.
    if pts is None and pts_str is None:
        raise ValueError(
            "Can cung cap 4 toa do goc qua tham so --pts (x1,y1,x2,y2,x3,y3,x4,y4) "
            "khi su dung anh thuc. Vi du:\n"
            "  python day4_task43.py anh.jpg 150,100,450,120,420,280,120,260"
        )

    if pts_str is not None:
        pts = parse_pts(pts_str)

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
