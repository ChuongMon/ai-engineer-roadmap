from __future__ import annotations

import argparse
import sys
from pathlib import Path

from image_inspector.scanner import scan_folder
from image_inspector.report import build_report, write_report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="image-inspector",
        description="Doc anh trong mot thu muc bang Pillow va xuat thong ke ra JSON.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Duong dan thu muc chua anh (chi doc truc tiep, khong doc thu muc con).",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Duong dan file JSON xuat ket qua (vd: ./reports/report.json).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_folder = Path(args.input)
    output_path = Path(args.output)

    try:
        scan_result = scan_folder(input_folder)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    report = build_report(scan_result)
    out = write_report(report, output_path)

    summary = report["summary"]
    print(f"[OK] Da ghi bao cao: {out}")
    print(f"  Tong file: {summary['total_files']}")
    print(f"  Anh hop le: {summary['valid_images']}")
    print(f"  Anh loi:    {summary['error_images']}")
    print(f"  Khong anh:  {summary['non_image_files']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
