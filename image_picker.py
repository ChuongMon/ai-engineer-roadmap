"""Windows-friendly image-folder selection shared by Day 4 demos."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter.filedialog import askdirectory

import cv2


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
    ".webp",
}


def first_readable_image(folder: Path) -> Path:
    """Return the first readable image, ordered by filename."""
    if not folder.is_dir():
        raise FileNotFoundError(f"Thu muc khong ton tai: {folder}")

    candidates = sorted(
        (
            path
            for path in folder.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ),
        key=lambda path: (path.name.casefold(), path.name),
    )
    for path in candidates:
        if cv2.imread(str(path), cv2.IMREAD_COLOR) is not None:
            return path

    raise FileNotFoundError(
        f"Khong tim thay anh hop le trong thu muc: {folder}"
    )


def select_first_image_from_folder(title: str) -> Path | None:
    """Ask for an image folder and return its first readable image.

    Return None when the folder dialog is cancelled.
    """
    root = tk.Tk()
    root.withdraw()
    try:
        selected_folder = askdirectory(title=title, parent=root)
    finally:
        root.destroy()

    if not selected_folder:
        return None
    return first_readable_image(Path(selected_folder))
