"""Main module - chay pipeline xu ly anh tu dau den cuoi."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

from loader import ImageData, load_image, save_image
from preprocessing import preprocess_pipeline
from roi import crop_and_perspective, validate_quadrilateral


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="cv-pipeline",
        description="Image Preprocessing Pipeline - doc anh, xu ly, xuat ket qua.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Duong den file anh dau vao.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Thu muc luu file ket qua (mac dinh: outputs).",
    )
    parser.add_argument(
        "--pts",
        default=None,
        help="Toa do 4 diem perspective (x1,y1,x2,y2,x3,y3,x4,y4), neu muon chinh perspective.",
    )
    return parser.parse_args(argv)


def validate_pts_in_image(pts: np.ndarray, img_shape: tuple[int, int]) -> None:
    """Kiem tra tat ca toa do 4 diem nam trong khoang anh."""
    h, w = img_shape[:2]
    for i, (x, y) in enumerate(pts):
        if not (0 <= x < w and 0 <= y < h):
            raise ValueError(f"Diem {i} ({x},{y}) nam ngoai anh (w={w}, h={h})")


def run_pipeline(
    input_path: str | Path,
    output_dir: str | Path = "outputs",
    pts: str | None = None,
) -> dict[str, object]:
    """Chay toan bo pipeline xu ly anh.

    Args:
        input_path: Duong den anh dau vao.
        output_dir: Thu muc luu ket qua.
        pts: Chuoi toa do 8 so, hoac None.

    Returns:
        Dict ten buoc -> duong dan file da luu.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. Doc anh
    image_data: ImageData = load_image(input_path)
    image = image_data.array

    # 2. Preprocessing pipeline
    results = preprocess_pipeline(image)

    saved: dict[str, object] = {}

    # Luu tat ca buoc preprocessing
    for name, arr in results.items():
        saved[name] = save_image(arr, output_path / f"{name}.png")

    # 3. ROI + Perspective (neu co toa do)
    if pts:
        coords = [int(v) for v in pts.split(",")]
        if len(coords) != 8:
            raise ValueError("Can dung 8 toa do (x1,y1,...,x4,y4)")
        pts_array = np.array(
            [
                [coords[0], coords[1]],
                [coords[2], coords[3]],
                [coords[4], coords[5]],
                [coords[6], coords[7]],
            ],
            dtype=np.float32,
        )

        # Validate toa do nam trong anh
        validate_pts_in_image(pts_array, image.shape)

        # Validate quadrilateral
        validate_quadrilateral(pts_array, image.shape)

        roi, corrected = crop_and_perspective(image, pts_array)
        saved["roi"] = save_image(roi, output_path / "roi.png")
        saved["perspective"] = save_image(corrected, output_path / "perspective.png")
    else:
        saved["roi"] = None
        saved["perspective"] = None

    return saved


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        saved = run_pipeline(args.input, args.output_dir, args.pts)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    print(f"[OK] Pipeline hoan tat. Luu vao: {args.output_dir}")
    for name, path in saved.items():
        if path is not None:
            print(f"  - {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
