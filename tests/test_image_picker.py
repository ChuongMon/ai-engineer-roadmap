from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import pytest

from image_picker import first_readable_image, select_first_image_from_folder


def test_selects_first_readable_image_by_filename(tmp_path: Path) -> None:
    image = np.zeros((8, 8, 3), dtype=np.uint8)
    cv2.imwrite(str(tmp_path / "zebra.png"), image)
    cv2.imwrite(str(tmp_path / "Alpha.jpg"), image)
    (tmp_path / "notes.txt").write_text("not an image", encoding="utf-8")

    with patch("image_picker.tk.Tk") as tk_mock, patch(
        "image_picker.askdirectory", return_value=str(tmp_path)
    ) as dialog_mock:
        selected = select_first_image_from_folder("Choose an image folder")

    assert selected == tmp_path / "Alpha.jpg"
    dialog_mock.assert_called_once_with(
        title="Choose an image folder",
        parent=tk_mock.return_value,
    )
    tk_mock.return_value.withdraw.assert_called_once()
    tk_mock.return_value.destroy.assert_called_once()


def test_cancelled_folder_dialog_returns_none() -> None:
    with patch("image_picker.tk.Tk") as tk_mock, patch(
        "image_picker.askdirectory", return_value=""
    ):
        selected = select_first_image_from_folder("Choose an image folder")

    assert selected is None
    tk_mock.return_value.destroy.assert_called_once()


def test_empty_folder_has_clear_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Khong tim thay anh hop le"):
        first_readable_image(tmp_path)
