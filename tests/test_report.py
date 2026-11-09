from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from image_inspector.scanner import scan_folder
from image_inspector.report import build_report, write_report


class TestReport(unittest.TestCase):

    def _make_scan_result(self):
        return {
            "input_folder": "C:/fake",
            "total_files": 3,
            "valid_images": ["ok.jpg"],
            "error_images": [{"file": "bad.png", "reason": "khong doc duoc"}],
            "non_image_files": ["note.txt"],
            "checked_details": "Pillow verify",
        }

    def test_build_report_co_dung_schema(self):
        """Output JSON report co dung schema yeu cau."""
        report = build_report(self._make_scan_result())
        for key in ("report_type", "created_at", "input_folder", "method", "summary", "valid_images", "error_images", "non_image_files"):
            self.assertIn(key, report)
        summary = report["summary"]
        for key in ("total_files", "image_files", "valid_images", "error_images", "non_image_files"):
            self.assertIn(key, summary)
        self.assertEqual(summary["total_files"], 3)
        self.assertEqual(summary["image_files"], 2)
        self.assertEqual(summary["valid_images"], 1)
        self.assertEqual(summary["error_images"], 1)
        self.assertEqual(summary["non_image_files"], 1)

    def test_build_report_valid_va_error_co_dung_cau_truc(self):
        """valid_images va error_images co file/ok/reason dung."""
        report = build_report(self._make_scan_result())
        self.assertEqual(report["valid_images"][0]["file"], "ok.jpg")
        self.assertTrue(report["valid_images"][0]["ok"])
        self.assertEqual(report["error_images"][0]["file"], "bad.png")
        self.assertFalse(report["error_images"][0]["ok"])
        self.assertIn("reason", report["error_images"][0])

    def test_write_report_tu_tao_output_folder(self):
        """write_report phai tu tao thu muc output neu chua ton tai."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "nested" / "deep" / "report.json"
            self.assertFalse(out.parent.exists())
            written = write_report({"hello": "world"}, out)
            self.assertTrue(written.exists())
            self.assertTrue(out.parent.exists())
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["hello"], "world")

    def test_write_report_ghi_de_file_cu(self):
        """write_report ghi de (overwrite) file JSON cu."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "report.json"
            write_report({"v": 1}, out)
            write_report({"v": 2}, out)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["v"], 2)

    def test_report_tich_hop_scan_folder(self):
        """Tich hop: scan folder thuc -> build_report -> JSON dung."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            Image.new("RGB", (5, 5), (0, 0, 0)).save(tmp / "ok.png")
            (tmp / "bad.jpg").write_bytes(b"broken")
            (tmp / "readme.txt").write_text("x")
            scan = scan_folder(tmp)
            report = build_report(scan)
            self.assertEqual(report["summary"]["total_files"], 3)
            self.assertEqual(report["summary"]["valid_images"], 1)
            self.assertEqual(report["summary"]["error_images"], 1)
            self.assertEqual(report["summary"]["non_image_files"], 1)


if __name__ == "__main__":
    unittest.main()
