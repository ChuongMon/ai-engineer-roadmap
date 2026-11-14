"""Task 4.2 - OpenCV Preprocessing.

Thuc hien tren cung mot anh:
  - Grayscale conversion
  - Gaussian blur (trước và sau threshold/Canny de so sanh)
  - Thresholding (binary + Otsu)
  - Adaptive Threshold
  - Canny edge detection
  - Morphological operations: Erosion, Dilation, Opening, Closing
    * Tren Canny edge map
    * Tren binary threshold image (de so sanh cho OCR)

Chay: python day4_task42.py [duong_dan_anh]
Neu khong co anh, chuong trinh su dung anh mau tu Task 4.1 hoac tao moi.
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


def load_image(path: Path | None = None) -> np.ndarray:
    """Doc anh thanh NumPy array bang OpenCV."""
    if path is None:
        path = Path("task41_synthetic.png")
    if not path.exists():
        # Tao anh mau neu chua co
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        img[0:400, 0:600] = (50, 50, 50)
        img[50:200, 50:250] = (0, 255, 0)
        img[50:200, 350:550] = (0, 0, 255)
        img[250:380, 200:400] = (255, 0, 0)
        cv2.line(img, (0, 200), (600, 200), (255, 255, 255), 3)
        cv2.imwrite(str(path), img)
        safe_print(f"[INFO] Khong co anh dau vao. Da tao anh mau: {path}")
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Khong the doc anh: {path}")
    return img


def save(img: np.ndarray, out_dir: Path, name: str) -> Path:
    """Luu anh va tra ve duong dan."""
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / name
    cv2.imwrite(str(p), img)
    safe_print(f"[OK] Luu: {p}  shape={img.shape} dtype={img.dtype}")
    return p


def preprocessing_pipeline(img: np.ndarray, out_dir: Path) -> dict[str, Path]:
    """Chay cac phuong phap preprocessing tren cung mot anh va luu ket qua."""
    outputs: dict[str, Path] = {}

    # 1. Grayscale conversion
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    outputs["grayscale"] = save(gray, out_dir, "task42_grayscale.png")

    # 2. Gaussian blur (tren grayscale)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    outputs["gaussian_blur"] = save(blurred, out_dir, "task42_gaussian_blur.png")

    # 3. Thresholding tren GRAY (khong blur) va tren BLURRED (co blur)
    _, thresh_binary_gray = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    outputs["threshold_binary_gray"] = save(
        thresh_binary_gray, out_dir, "task42_threshold_binary_gray.png"
    )

    _, thresh_binary_blur = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
    outputs["threshold_binary_blur"] = save(
        thresh_binary_blur, out_dir, "task42_threshold_binary_blur.png"
    )

    _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    outputs["threshold_otsu"] = save(thresh_otsu, out_dir, "task42_threshold_otsu.png")

    # 4. Adaptive Threshold (tren gray)
    adaptive_mean = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
    )
    outputs["adaptive_mean"] = save(adaptive_mean, out_dir, "task42_adaptive_mean.png")

    adaptive_gauss = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    outputs["adaptive_gaussian"] = save(
        adaptive_gauss, out_dir, "task42_adaptive_gaussian.png"
    )

    # 5. Canny edge detection
    edges_gray = cv2.Canny(gray, 100, 200)
    outputs["canny_gray"] = save(edges_gray, out_dir, "task42_canny_gray.png")

    edges_blur = cv2.Canny(blurred, 100, 200)
    outputs["canny_blur"] = save(edges_blur, out_dir, "task42_canny_blur.png")

    # 6. Morphological operations
    kernel = np.ones((3, 3), np.uint8)

    # 6a. Morphology tren CANNY edge map
    eroded_canny = cv2.erode(edges_gray, kernel, iterations=1)
    outputs["erosion_canny"] = save(eroded_canny, out_dir, "task42_erosion_canny.png")

    dilated_canny = cv2.dilate(edges_gray, kernel, iterations=1)
    outputs["dilation_canny"] = save(dilated_canny, out_dir, "task42_dilation_canny.png")

    opened_canny = cv2.morphologyEx(edges_gray, cv2.MORPH_OPEN, kernel)
    outputs["opening_canny"] = save(opened_canny, out_dir, "task42_opening_canny.png")

    closed_canny = cv2.morphologyEx(edges_gray, cv2.MORPH_CLOSE, kernel)
    outputs["closing_canny"] = save(closed_canny, out_dir, "task42_closing_canny.png")

    # 6b. Morphology tren BINARY threshold image (de so sanh cho OCR)
    eroded_bin = cv2.erode(thresh_binary_gray, kernel, iterations=1)
    outputs["erosion_binary"] = save(eroded_bin, out_dir, "task42_erosion_binary.png")

    dilated_bin = cv2.dilate(thresh_binary_gray, kernel, iterations=1)
    outputs["dilation_binary"] = save(dilated_bin, out_dir, "task42_dilation_binary.png")

    opened_bin = cv2.morphologyEx(thresh_binary_gray, cv2.MORPH_OPEN, kernel)
    outputs["opening_binary"] = save(opened_bin, out_dir, "task42_opening_binary.png")

    closed_bin = cv2.morphologyEx(thresh_binary_gray, cv2.MORPH_CLOSE, kernel)
    outputs["closing_binary"] = save(closed_bin, out_dir, "task42_closing_binary.png")

    # 7. Anh so sanh hien tuy: canny vs binary truoc/sau morphology
    cmp_canny = np.hstack([edges_gray, eroded_canny, dilated_canny])
    outputs["compare_canny_morphology"] = save(
        cmp_canny, out_dir, "task42_compare_canny_morphology.png"
    )

    cmp_binary = np.hstack([thresh_binary_gray, eroded_bin, dilated_bin])
    outputs["compare_binary_morphology"] = save(
        cmp_binary, out_dir, "task42_compare_binary_morphology.png"
    )

    return outputs


def summarize(outputs: dict[str, Path]) -> None:
    """In tom ttat cac file da xuat."""
    safe_print("\n" + "=" * 60)
    safe_print("TOM TAT CAC PHUONG PHUOC PREPROCESSING")
    safe_print("=" * 60)
    for name, p in outputs.items():
        safe_print(f"  - {name:32s} -> {p.name}")
    safe_print("=" * 60 + "\n")


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    out_dir = Path("outputs/task42")

    img = load_image(path)
    safe_print(f"\nAnh goc: {img.shape}, dtype={img.dtype}")
    outputs = preprocessing_pipeline(img, out_dir)
    summarize(outputs)
    safe_print(f"[HOAN TAT] Tat ca file ket qua duoc luu o: {out_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
