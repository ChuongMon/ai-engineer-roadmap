from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from image_inspector.scanner import scan_folder, is_image_file, read_image


class TestScanner(unittest.TestCase):

    def test_scan_folder_voi_folder_rong(self):
        """scan_folder voi folder rong tra ve total_files=0 va danh sach rong."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = scan_folder(Path(tmpdir))
            self.assertEqual(result["total_files"], 0)
            self.assertEqual(result["valid_images"], [])
            self.assertEqual(result["error_images"], [])
            self.assertEqual(result["non_image_files"], [])
            self.assertIsNone(result["checked_details"])

    def test_scan_folder_chua_anh_hop_le_va_anh_hong(self):
        """scan_folder phan loai dung anh hop le va anh hong."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            Image.new("RGB", (10, 10), (255, 0, 0)).save(tmp / "ok.jpg")
            (tmp / "bad.png").write_bytes(b"not-a-real-image")
            result = scan_folder(tmp)
            self.assertEqual(result["total_files"], 2)
            self.assertIn("ok.jpg", result["valid_images"])
            self.assertEqual(len(result["error_images"]), 1)
            self.assertEqual(result["error_images"][0]["file"], "bad.png")
            self.assertTrue(result["error_images"][0]["reason"])

    def test_scan_folder_khong_scan_thu_muc_con(self):
        """Nested folders khong bi scan (chi quet truc tiep)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            sub = tmp / "subdir"
            sub.mkdir()
            Image.new("RGB", (5, 5), (0, 0, 0)).save(sub / "nested.jpg")
            (tmp / "root.txt").write_text("hello")
            result = scan_folder(tmp)
            self.assertEqual(result["total_files"], 1)
            self.assertEqual(result["non_image_files"], ["root.txt"])
            self.assertEqual(result["valid_images"], [])
            self.assertNotIn("nested.jpg", [p for p in result["valid_images"]])

    def test_scan_folder_invalid_input_path(self):
        """Duong dan khong ton tai phai raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            scan_folder(Path("D:/duong/dan/khong/ton/tai/abc123xyz"))

    def test_scan_folder_input_khong_phai_thu_muc(self):
        """Duong dan tro toi file (khong phai thu muc) phai raise NotADirectoryError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "afile.txt"
            file_path.write_text("x")
            with self.assertRaises(NotADirectoryError):
                scan_folder(file_path)

    def test_is_image_file_nhan_dien_duoi(self):
        """is_image_file nhan dien dung duoi anh va tu choi file khac."""
        self.assertTrue(is_image_file("a.jpg"))
        self.assertTrue(is_image_file("A.PNG"))
        self.assertTrue(is_image_file("b.webp"))
        self.assertFalse(is_image_file("note.txt"))
        self.assertFalse(is_image_file("archive.zip"))

    def test_read_image_tra_ve_checked_details(self):
        """read_image tra ve checked_details khi doc anh hop le."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "ok.png"
            Image.new("RGB", (3, 3), (0, 255, 0)).save(path)
            ok, reason, checked = read_image(path)
            self.assertTrue(ok)
            self.assertIsNone(reason)
            self.assertIsNotNone(checked)


if __name__ == "__main__":
    unittest.main()
