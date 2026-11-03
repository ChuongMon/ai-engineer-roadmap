import os
import tempfile
import unittest
from PIL import Image

from bao_cao_anh import is_image_file, read_image


class TestBaoCaoAnh(unittest.TestCase):

    def test_is_image_file_chap_nhan_cac_duoi_anh(self):
        """Ham is_image_file phai tra ve True voi cac duoi anh ho tro."""
        self.assertTrue(is_image_file("anh.jpg"))
        self.assertTrue(is_image_file("anh.JPG"))
        self.assertTrue(is_image_file("anh.png"))
        self.assertTrue(is_image_file("anh.PNG"))
        self.assertTrue(is_image_file("anh.bmp"))
        self.assertTrue(is_image_file("anh.webp"))

    def test_is_image_file_tu_choi_duoi_khong_phai_anh(self):
        """Ham is_image_file phai tra ve False voi duoi khong phai anh."""
        self.assertFalse(is_image_file("file.txt"))
        self.assertFalse(is_image_file("file.pdf"))
        self.assertFalse(is_image_file("file.docx"))
        self.assertFalse(is_image_file("file"))

    def test_read_image_tra_ve_ok_cho_anh_hop_le(self):
        """read_image phai tra ve ok=True voi anh hop le."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "hop_le.png")
            Image.new("RGB", (10, 10), (255, 0, 0)).save(path)
            ok, reason, checked = read_image(path)
            self.assertTrue(ok)
            self.assertIsNone(reason)
            self.assertIsNotNone(checked)

    def test_read_image_tra_ve_loi_cho_anh_hong(self):
        """read_image phai tra ve ok=False va co ly do voi anh hong."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "hong.jpg")
            with open(path, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n" + b"du lieu khong chinh xac")
            ok, reason, checked = read_image(path)
            self.assertFalse(ok)
            self.assertIsNotNone(reason)
            self.assertIsNotNone(checked)
            lowered = reason.lower()
            self.assertTrue("khong" in lowered or "loi" in lowered or "ly do" in lowered)


if __name__ == "__main__":
    unittest.main()
