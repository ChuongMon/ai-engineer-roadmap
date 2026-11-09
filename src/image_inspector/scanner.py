from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

IMAGE_EXTENSIONS: set[str] = {
    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif",
    ".webp", ".ico", ".ppm", ".pgm", ".pbm", ".pcx", ".xbm",
}


def is_image_file(filename: str) -> bool:
    """Return True if filename has a supported image extension."""
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS


def read_image(filepath: Path) -> tuple[bool, str | None, str]:
    """Read and verify an image with Pillow.

    Returns (ok, reason, checked).
    """
    checked = "Mo file bang Pillow (Image.open) + verify() de xac thuc du lieu anh."
    try:
        with Image.open(filepath) as img:
            img.verify()
        return True, None, checked
    except UnidentifiedImageError as e:
        reason = f"Khong nhan duoc dinh dang anh (UnidentifiedImageError): {e}"
        repro = f"Cach tai hien: Image.open(r'{filepath}') -> PIL khong nhan dinh dang file."
        return False, f"{reason} | {repro}", checked
    except OSError as e:
        reason = f"Loi doc anh (OSError): {e}"
        repro = f"Cach tai hien: Image.open(r'{filepath}') -> OSError khi doc file."
        return False, f"{reason} | {repro}", checked
    except Exception as e:
        reason = f"Loi khong xac dinh: {e}"
        repro = f"Cach tai hien: Image.open(r'{filepath}') -> Ngoai le khong xac dinh."
        return False, f"{reason} | {repro}", checked


def scan_folder(input_folder: Path) -> dict[str, Any]:
    """Scan only the direct children of input_folder (no recursion).

    Returns a dict with keys: input_folder, total_files, valid_images,
    error_images, non_image_files, checked_details.
    Raises FileNotFoundError if input_folder does not exist.
    NotADirectoryError if input_folder is not a directory.
    """
    input_folder = Path(input_folder)
    if not input_folder.exists():
        raise FileNotFoundError(f"Duong dan khong ton tai: {input_folder}")
    if not input_folder.is_dir():
        raise NotADirectoryError(f"Duong dan khong phai thu muc: {input_folder}")

    valid_images: list[str] = []
    error_images: list[dict[str, str]] = []
    non_image_files: list[str] = []
    total_files = 0
    checked_details: str | None = None

    for entry in sorted(input_folder.iterdir(), key=lambda p: p.name.lower()):
        if not entry.is_file():
            continue
        total_files += 1
        name = entry.name
        if not is_image_file(name):
            non_image_files.append(name)
            continue
        ok, reason, checked = read_image(entry)
        if checked_details is None:
            checked_details = checked
        if ok:
            valid_images.append(name)
        else:
            error_images.append({"file": name, "reason": reason or ""})

    return {
        "input_folder": str(input_folder.resolve()),
        "total_files": total_files,
        "valid_images": valid_images,
        "error_images": error_images,
        "non_image_files": non_image_files,
        "checked_details": checked_details,
    }
