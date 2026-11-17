import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

from bao_cao_anh import (
    build_report,
    is_image_file,
    main,
    read_image,
    scan_folder,
)


class TestBaoCaoAnh(unittest.TestCase):

    def test_is_image_file_chap_nhan_cac_duoi_anh(self):
        """is_image_file phai tra ve True voi cac duoi anh ho tro."""
        self.assertTrue(is_image_file("anh.jpg"))
        self.assertTrue(is_image_file("anh.JPG"))
        self.assertTrue(is_image_file("anh.png"))
        self.assertTrue(is_image_file("anh.PNG"))
        self.assertTrue(is_image_file("anh.bmp"))
        self.assertTrue(is_image_file("anh.webp"))

    def test_is_image_file_tu_choi_duoi_khong_phai_anh(self):
        """is_image_file phai tra ve False voi duoi khong phai anh."""
        self.assertFalse(is_image_file("file.txt"))
        self.assertFalse(is_image_file("file.pdf"))
        self.assertFalse(is_image_file("file.docx"))
        self.assertFalse(is_image_file("file"))
        self.assertFalse(is_image_file(""))

    def test_read_image_tra_ve_ok_cho_anh_hop_le(self):
        """read_image phai tra ve ok=True voi anh hop le."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "hop_le.png"
            Image.new("RGB", (10, 10), (255, 0, 0)).save(path)
            ok, reason, checked = read_image(path)
            self.assertTrue(ok)
            self.assertIsNone(reason)
            self.assertIsNotNone(checked)

    def test_read_image_tra_ve_loi_cho_anh_hong(self):
        """read_image phai tra ve ok=False va co ly do voi anh hong."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "hong.jpg"
            path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"du lieu khong chinh xac")
            ok, reason, checked = read_image(path)
            self.assertFalse(ok)
            self.assertIsNotNone(reason)
            self.assertIsNotNone(checked)
            lowered = reason.lower()
            self.assertTrue("khong" in lowered or "loi" in lowered or "ly do" in lowered)

    def test_scan_folder_dem_dung_so_luong(self):
        """scan_folder phai dem dung so luong anh hop le, anh hong, file khong anh."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            Image.new("RGB", (5, 5), (0, 0, 0)).save(tmp / "ok1.jpg")
            Image.new("RGB", (5, 5), (0, 0, 0)).save(tmp / "ok2.png")
            (tmp / "bad.jpg").write_bytes(b"not an image")
            (tmp / "note.txt").write_text("khong phai anh")
            valid, errors, non_images, total, _ = scan_folder(tmp)
            self.assertEqual(total, 4)
            self.assertEqual(len(valid), 2)
            self.assertEqual(len(errors), 1)
            self.assertEqual(len(non_images), 1)

    def test_scan_folder_khong_doc_thu_muc_con(self):
        """scan_folder KHONG duoc doc file trong thu muc con."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            sub = tmp / "sub"
            sub.mkdir()
            Image.new("RGB", (5, 5), (0, 0, 0)).save(sub / "subimg.jpg")
            (tmp / "goc.txt").write_text("file goc")
            valid, errors, non_images, total, _ = scan_folder(tmp)
            self.assertEqual(total, 1)
            self.assertEqual(len(valid), 0)
            self.assertEqual(len(non_images), 1)
            self.assertNotIn("subimg.jpg", non_images)

    def test_build_report_chua_cac_phan_khoa(self):
        """build_report phai chua tong ket, danh sach anh khong loi, danh sach anh loi."""
        report = build_report(
            Path("/tmp"),
            "bao_cao_anh.txt",
            ["ok.jpg"],
            [("bad.jpg", "Loi test")],
            ["note.txt"],
            3,
            "Mo file bang Pillow (Image.open) + verify() de xac thuc du lieu anh.",
        )
        self.assertIn("TONG KET", report)
        self.assertIn("DANH SACH ANH KHONG LOI", report)
        self.assertIn("DANH SACH ANH BI LOI", report)
        self.assertIn("ok.jpg", report)
        self.assertIn("bad.jpg", report)
        self.assertIn("note.txt", report)

    def test_scan_folder_tra_ve_checked_details_khong_none_khi_co_anh(self):
        """Khi co it nhat mot anh, checked_details phai khong None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            Image.new("RGB", (5, 5), (0, 0, 0)).save(tmp / "ok.jpg")
            valid, errors, non_images, total, checked = scan_folder(tmp)
            self.assertIsNotNone(checked)

    @patch("bao_cao_anh.tk.Tk")
    @patch("bao_cao_anh.askdirectory", return_value="")
    @patch("bao_cao_anh.scan_folder")
    def test_main_cancel_selection_exits_without_report(
        self, scan_folder_mock, askdirectory_mock, tk_mock
    ):
        """Huy chon thu muc phai thoat em va khong tao report."""
        root = tk_mock.return_value

        result = main(["--output", "report.txt"])

        self.assertEqual(result, 0)
        askdirectory_mock.assert_called_once_with(
            title="Chon thu muc chua anh can thong ke",
            parent=root,
        )
        root.withdraw.assert_called_once()
        root.destroy.assert_called_once()
        scan_folder_mock.assert_not_called()

    @patch("bao_cao_anh.tk.Tk")
    @patch("bao_cao_anh.askdirectory")
    def test_main_scans_selected_folder_and_writes_report(
        self, askdirectory_mock, tk_mock
    ):
        """Thu muc chon trong dialog duoc dung de scan va luu report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            selected_folder = Path(tmpdir)
            Image.new("RGB", (5, 5), (0, 0, 0)).save(selected_folder / "ok.png")
            askdirectory_mock.return_value = str(selected_folder)

            result = main(["--output", "custom-report.txt"])

            report_path = selected_folder / "custom-report.txt"
            self.assertEqual(result, 0)
            self.assertTrue(report_path.is_file())
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("Thu dau vao: " + str(selected_folder), report)
            self.assertIn("ok.png", report)
            tk_mock.return_value.destroy.assert_called_once()


if __name__ == "__main__":
    unittest.main()
