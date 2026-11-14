"""Task 4.1 - NumPy Image Fundamentals.

Chuong trinh minh hoa:
  - Doc anh thanh NumPy array (OpenCV).
  - shape, dtype, ndim.
  - Truy cap pixel va ROI (co kiem tra kich thuc).
  - Crop, resize, transpose.
  - Chuyen doi RGB/BGR/Grayscale (luu dung mau).
  - Gia thuyet tai sao OpenCV doc anh theo BGR.

Chay: python day4_task41.py [duong_dan_anh]
Neu khong co anh dau vao, chuong trinh tao anh mau tao dong de minh hoa.
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


def create_synthetic_image(path: Path) -> np.ndarray:
    """Tao anh mau co cac vung mau phan biet de minh hoa."""
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    img[0:400, 0:600] = (50, 50, 50)
    img[50:200, 50:250] = (0, 255, 0)      # vung xanh luc (ROI)
    img[50:200, 350:550] = (0, 0, 255)     # vung do
    img[250:380, 200:400] = (255, 0, 0)    # vung xanh duong
    cv2.line(img, (0, 200), (600, 200), (255, 255, 255), 3)
    cv2.imwrite(str(path), img)
    return img


def load_image(path: Path | None = None) -> np.ndarray:
    """Doc anh thanh NumPy array bang OpenCV."""
    if path is None or not path.exists():
        synth = Path("task41_synthetic.png")
        img = create_synthetic_image(synth)
        safe_print(f"[INFO] Khong co anh dau vao. Da tao anh mau: {synth}")
        return img
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Khong the doc anh: {path}")
    return img


def validate_image_min_size(img: np.ndarray, min_h: int, min_w: int) -> None:
    """Kiem tra anh co kich thuc it thap nhat min_h x min_w."""
    h, w = img.shape[:2]
    if h < min_h or w < min_w:
        raise ValueError(
            f"Anh qua nho: ({h}x{w}), can it thap nhat ({min_h}x{min_w})"
        )


def access_pixel_and_roi(img: np.ndarray) -> None:
    """Truy cap mot pixel va mot vung ROI voi kiem tra kich thuc."""
    h, w = img.shape[:2]
    validate_image_min_size(img, 201, 251)

    # Pixel o vi tri (100, 100)
    px = img[100, 100]
    safe_print(f"\n[PIXEL] tai (hang=100, cot=100) = BGR {px.tolist()}")

    # ROI vung xanh luc (50:200, 50:250)
    roi = img[50:200, 50:250]
    safe_print(
        f"[ROI]  vung (50:200, 50:250) co shape {roi.shape}, "
        f"mau trung binh = {roi.mean(axis=(0, 1)).round(1).tolist()}"
    )


def crop_resize_transpose(img: np.ndarray, out_dir: Path) -> None:
    """Thuc hien crop, resize, transpose va luu ket qua."""
    # Crop: lay nua trai cua anh
    crop = img[:, : img.shape[1] // 2]
    cv2.imwrite(str(out_dir / "task41_crop.png"), crop)
    safe_print(f"\n[CROP]  nua trai -> {crop.shape}, luu task41_crop.png")

    # Resize: thu nho xuong 300x200
    resized = cv2.resize(img, (300, 200), interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(out_dir / "task41_resized.png"), resized)
    safe_print(f"[RESIZE] 300x200 -> {resized.shape}, luu task41_resized.png")

    # Transpose: dao chuyen hang/cot (kieu ma tran)
    transposed = np.transpose(img, (1, 0, 2))
    cv2.imwrite(str(out_dir / "task41_transposed.png"), transposed)
    safe_print(f"[TRANSPOSE] dao hang/cot -> {transposed.shape}, luu task41_transposed.png")


def convert_color_spaces(img: np.ndarray, out_dir: Path) -> None:
    """Chuyen doi RGB/BGR/Grayscale va luu DUNG MAU.

    OpenCV doc theo BGR. cv2.imwrite luu theo BGR, nen neu muon luu anh RGB
    thuc su ta can chuyen ngoc lai BGR truoc khi ghi, hoac su dung Matplotlib.
    """
    # BGR -> RGB (de hien thi thuan thieng voi matplotlib/PIL)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Luu RGB bang OpenCV can chuyen ngoc lai BGR, nguoc lai mau se bi dao ngoc
    cv2.imwrite(
        str(out_dir / "task41_rgb.png"), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    )
    safe_print(f"\n[COLOR] BGR -> RGB, luu task41_rgb.png (da chuyen ngoc BGR de ghi dung mau)")

    # BGR -> Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(str(out_dir / "task41_gray.png"), gray)
    safe_print(f"[COLOR] BGR -> GRAY, shape {gray.shape}, luu task41_gray.png")

    # Grayscale -> BGR (1 kenh -> 3 kenh)
    gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    cv2.imwrite(str(out_dir / "task41_gray2bgr.png"), gray_bgr)
    safe_print(f"[COLOR] GRAY -> BGR, shape {gray_bgr.shape}, luu task41_gray2bgr.png")


def explain_bgr() -> None:
    """Gia thuyet tai sao OpenCV doc anh theo BGR."""
    safe_print("\n" + "=" * 70)
    safe_print("TAI SAO OPENCV DOC ANH THEO BGR KHONG PHAI RGB?")
    safe_print("=" * 70)
    safe_print(
        "- Lich su: OpenCV duoc xay dung tren cep chinh thuc cua Intel (OpenCV "
        "1.0 nam 2006). Truoc do, cac thu vien xu ly anh Co So Viet Nam / "
        "moi truong C co su dung thu tu Byte Blue-Green-Red (BGR) vi do la "
        "thu tu luu tru mac dinh cua nhieu dinh dang va thiet bi capture "
        "trong thoi ky do (VD: Video for Windows, VfW)."
    )
    safe_print(
        "- Dinh dang file: BMP luu tru pixel theo thu tu BGR. Vì OpenCV ban dau "
        "muon doc file anh thuan thieng voi bo nho / co so du lieu hinh anh co "
        "san, chung noi chuyen giu BGR va RGB khong can bo nho them."
    )
    safe_print(
        "- Bo nho: Mot anh RGB va mot anh BGR luu cung so luong byte. Chuyen doi "
        "giua chung chi can hoan doi chi so kenh (channel swap), chi tốn O(n) "
        "thoi gian va khong can bo nho them neu lam in-place."
    )
    safe_print(
        "- Mat khac ket qua neu luan tuong: Neu doc anh bang OpenCV (BGR) nhung "
        "xu ly hoac hien thi nhu RGB (matplotlib, PIL, hien thi web), muc mau "
        "se bi dao ngoc: vung xanh duong hien thi thanh do va nguoc lai."
    )
    safe_print(
        "- Khuyen khich: Luon biet rang OpenCV tra ve BGR. Can can hanh "
        "cv2.cvtColor(img, cv2.COLOR_BGR2RGB) truoc khi hien thi boi "
        "matplotlib/PIL hoac gui sang model duoc huon voi RGB."
    )
    safe_print("=" * 70 + "\n")


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    out_dir = Path("outputs/task41")
    out_dir.mkdir(parents=True, exist_ok=True)

    img = load_image(path)
    show_array_info(img, "Anh goc (OpenCV doc)")
    access_pixel_and_roi(img)
    crop_resize_transpose(img, out_dir)
    convert_color_spaces(img, out_dir)
    explain_bgr()
    safe_print(f"\n[HOAN TAT] Tat ca file ket qua duoc luu o: {out_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
