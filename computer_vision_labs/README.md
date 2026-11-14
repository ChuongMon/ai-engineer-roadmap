# Computer Vision Labs — Day 4 Mini Project

Image Preprocessing Pipeline for OCR / computer vision applications.

## Cau truc

```
computer_vision_labs/
├── data/
│   └── sample.png           # Anh dau vao mau (nhan thung hang)
├── src/
│   ├── __init__.py
│   ├── loader.py            # Doc anh thanh NumPy array (+ metadata)
│   ├── preprocessing.py     # Grayscale, denoise, threshold, edge detection
│   ├── roi.py               # Crop ROI, perspective transform
│   └── main.py              # Pipeline chinh, CLI bang argparse
├── outputs/
│   ├── original.png
│   ├── grayscale.png
│   ├── denoised.png
│   ├── threshold.png
│   ├── edges.png
│   ├── roi.png
│   ├── perspective.png
│   └── before_after.png     # So sanh truoc/sau (de doc trong README)
├── tests/
│   └── test_pipeline.py     # 11 unit tests (pytest)
└── README.md
```

## Yeu cau he thong

- Python >= 3.10
- numpy, opencv-python, pytest

## Cai dat

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install numpy opencv-python pytest
```

(Linux/macOS: `source .venv/bin/activate`)

## Chay pipeline

```powershell
$env:PYTHONPATH = "computer_vision_labs/src"
.venv\Scripts\python computer_vision_labs/src/main.py --input computer_vision_labs/data/sample.png --output-dir computer_vision_labs/outputs
```

Neu muon chinh perspective (can 8 toa do 4 diem):

```powershell
.venv\Scripts\python computer_vision_labs/src/main.py `
  --input computer_vision_labs/data/sample.png `
  --output-dir computer_vision_labs/outputs `
  --pts 150,100,450,120,420,280,120,260
```

## Output sinh ra

| File | Mo ta |
|------|-------|
| `original.png` | Anh goc |
| `grayscale.png` | Chuyen sang xam |
| `denoised.png` | Bo loc Gaussian (lam muot) |
| `threshold.png` | Nhi phan hoa (Otsu) |
| `edges.png` | Phat hien canh Canny |
| `roi.png` | Cat vung quan trong (bounding box) |
| `perspective.png` | Chinh perspective (thang binh nhan) |
| `before_after.png` | So sanh truoc/sau (dung trong README) |

## Before / After

![Before / After](outputs/before_after.png)

Trai: anh goc co nhan bi nghiêng. Phai: anh da chinh perspective (thang binh), de de doc text / OCR.

## Chay unit tests

Co **11 unit tests** trong `computer_vision_labs/tests/test_pipeline.py`:

1. `test_load_image_returns_imagedata` — doc anh tra ve ImageData dung thuoc tinh.
2. `test_load_image_nonexistent_file_raises` — file khong ton tai -> FileNotFoundError.
3. `test_to_grayscale` — BGR -> Grayscale (2 chieu, uint8).
4. `test_denoise` — Gaussian blur giu nguyen shape/kieu du lieu.
5. `test_threshold_returns_binary` — Nhi phan chi co 0 va 255.
6. `test_edge_detect` — Canny edge dung shape/kieu du lieu.
7. `test_preprocess_pipeline_returns_all_steps` — Tra ve 5 buoc: original, grayscale, denoised, threshold, edges.
8. `test_crop_roi` — Cat ROI dung bounding box.
9. `test_order_points` — Sap xep 4 diem dung thu tu.
10. `test_perspective_transform` — Tra ve anh hinh chu nhat thang.
11. `test_save_image_creates_file` — Luu file va doc lai dung.

Lenh chay:

```powershell
$env:PYTHONPATH = "computer_vision_labs/src"
.venv\Scripts\python -m pytest computer_vision_labs/tests/ -v
```

Ket qua: **11 passed**.

## Cac phuong phap preprocessing da thuc hien

1. **Grayscale conversion** — `cv2.cvtColor(..., COLOR_BGR2GRAY)`
2. **Gaussian blur (denoise)** — `cv2.GaussianBlur(..., (5,5), 0)`
3. **Thresholding** — `cv2.threshold(..., THRESH_BINARY + THRESH_OTSU)`
4. **Canny edge detection** — `cv2.Canny(..., 100, 200)`
5. **ROI crop** — Cat theo bounding box
6. **Perspective transform** — `cv2.getPerspectiveTransform` + `cv2.warpPerspective`

## Thiet ke code

- `loader.py`: Chỉ đọc/lưu ảnh, không có business logic.
- `preprocessing.py`: Chỉ các hàm xử lý ảnh thuần túy (type hints, không I/O).
- `roi.py`: Chỉ crop và perspective transform.
- `main.py`: Chỉ điều phối (parse args, gọi các module, ghi file). Không chứa business logic.
- Tat ca ham co type hints, xu ly ngoai le (FileNotFoundError, ValueError).
