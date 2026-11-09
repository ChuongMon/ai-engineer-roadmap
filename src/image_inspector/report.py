from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_report(scan_result: dict[str, Any]) -> dict[str, Any]:
    """Build a JSON-serializable report from scan_folder() result."""
    valid = scan_result.get("valid_images", [])
    errors = scan_result.get("error_images", [])
    non_images = scan_result.get("non_image_files", [])
    checked = scan_result.get("checked_details")

    return {
        "report_type": "image_inspector",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_folder": scan_result.get("input_folder"),
        "method": checked,
        "summary": {
            "total_files": scan_result.get("total_files", 0),
            "image_files": len(valid) + len(errors),
            "valid_images": len(valid),
            "error_images": len(errors),
            "non_image_files": len(non_images),
        },
        "valid_images": [{"file": name, "ok": True} for name in valid],
        "error_images": [{"file": e["file"], "ok": False, "reason": e.get("reason", "")} for e in errors],
        "non_image_files": [{"file": name, "skipped": True, "reason": "Duoi file khong thuoc danh sach dinh dang anh ho tro."} for name in non_images],
    }


def write_report(report: dict[str, Any], output_path: Path) -> Path:
    """Write report as JSON to output_path, creating parent directories."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path
