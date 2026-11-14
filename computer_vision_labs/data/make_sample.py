"""Tao anh mau cho data/ (chay mot lan de tao sample.png)."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

if __name__ == "__main__":
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    img[0:400, 0:600] = (240, 240, 240)

    # Ve mot nhan bi nghiêng (mo phong nhan thùng hàng)
    pts = np.array([[150, 100], [450, 120], [420, 280], [120, 260]], dtype=np.int32)
    cv2.fillConvexPoly(img, pts, (255, 255, 255))

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "LABEL", (240, 190), font, 1.5, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.polylines(img, [pts], isClosed=True, color=(0, 0, 0), thickness=2)

    out = Path("data/sample.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), img)
    print(f"Da tao anh mau: {out}")
