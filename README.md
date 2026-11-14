# Image Inspector + CV Labs (Day 3 + Day 4) — Package + CLI + Tests

## 1. Gioi thieu
Project da duoc refactor thanh package Python `image_inspector` (Day 3) va bo lab Computer Vision (Day 4, Task 4.1–4.2).
- Quet anh trong **mot thu muc** (chi truc tiep, khong doc thu muc con) bang Pillow.
- Phan loai anh hop le / anh bi loi / file khong phai anh.
- Xuat bao cao **JSON** qua CLI.
- NumPy Image Fundamentals (Task 4.1): doc anh thanh array, shape/dtype/ndim, pixel & ROI, crop/resize/transpose, chuyen doi BGR/RGB/Grayscale, giai ly do OpenCV doc BGR.
- OpenCV Preprocessing (Task 4.2): Grayscale, Gaussian Blur, Thresholding (binary + Otsu), Adaptive Threshold, Canny edge, Morphological (Erosion, Dilation, Opening, Closing) tren cung mot anh.

## 2. Cau truc project
```
Homework1/
├── src/
│   └── image_inspector/
│       ├── __init__.py
│       ├── scanner.py      # scan folder, validate images (type hints)
│       ├── report.py       # tong hop du lieu va xuat JSON
│       └── cli.py          # nhan arguments va goi cac module
├── tests/
│   ├── test_scanner.py     # Day 3: 7 tests
│   ├── test_report.py      # Day 3: 5 tests
│   ├── test_task41.py      # Day 4 Task 4.1: 10 tests
│   └── test_task42.py      # Day 4 Task 4.2: 8 tests
├── outputs/                # thu muc output sinh ra (bi .gitignore bo qua)
├── reports/                # thu muc output JSON Day 3 (bi .gitignore bo qua)
├── pyproject.toml
├── requirements.txt        # Pillow, numpy, opencv-python, matplotlib, pytest
├── system_info.py          # xuat thong tin he thong JSON (stdlib only)
├── day4_task41.py          # Day 4 Task 4.1 demo script
├── day4_task42.py          # Day 4 Task 4.2 demo script
├── README.md
├── .gitignore
├── .github/workflows/tests.yml
└── bao_cao_anh.py, test_bao_cao_anh.py  # phien ban cu (giu de tham chieu)
```

## 3. Yeu cau he thong
- Python >= 3.10 (CI dung 3.12)
- Pillow, numpy, opencv-python, matplotlib, pytest (`requirements.txt`)

## 4. Cai dat
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
(Linux/macOS: `source .venv/bin/activate` va `python3 -m pip install -r requirements.txt`)

## 5. Chay CLI (package, Day 3)
Chay tu thu muc goc project, dat `PYTHONPATH=src` (hoac cai package editable `pip install -e .`):
```powershell
$env:PYTHONPATH = "src"
.venv\Scripts\python -m image_inspector.cli --input .\test_anh --output .\reports\report.json
```
Linux/macOS:
```bash
PYTHONPATH=src .venv/bin/python -m image_inspector.cli --input ./test_anh --output ./reports/report.json
```
Tham so:
- `--input` (bat buoc): thu muc chua anh (chi quet truc tiep).
- `--output` (bat buoc): duong dan file JSON xuat ket qua (thu muc cha duoc tu dong tao).

## 6. Schema JSON bao cao (Day 3)
`build_report()`/CLI xuat JSON gom: `report_type`, `created_at`, `input_folder`, `method`, `summary` (`total_files`, `image_files`, `valid_images`, `error_images`, `non_image_files`), `valid_images`, `error_images` (co `file`, `ok`, `reason`), `non_image_files`.

## 7. Day 4 — Task 4.1 (NumPy Image Fundamentals)
Chay demo:
```powershell
.venv\Scripts\python day4_task41.py [duong_dan_anh]
```
Neu khong co anh dau vao, chuong trinh tao anh mau `task41_synthetic.png`.

Noi dung:
- Doc anh thanh NumPy array (OpenCV).
- `shape`, `dtype`, `ndim`.
- Truy cap pixel va ROI.
- Crop, resize, transpose.
- Chuyen doi RGB/BGR/Grayscale.
- Gia thuyet tai sao OpenCV doc anh theo BGR (lich su, dinh dang BMP, bo nho, luu yen neu luan tuong).

File dau ra: `outputs/task41/` (crop, resized, transposed, rgb, gray, gray2bgr).

## 8. Day 4 — Task 4.2 (OpenCV Preprocessing)
Chay demo:
```powershell
.venv\Scripts\python day4_task42.py [duong_dan_anh]
```
Neu khong co anh dau vao, chuong trinh su dung/tao anh mau.

Cac phuong phap thuc hien tren **cung mot anh**:
1. Grayscale conversion
2. Gaussian blur
3. Thresholding (binary + Otsu)
4. Adaptive Threshold (mean + gaussian)
5. Canny edge detection
6. Morphological: Erosion, Dilation, Opening, Closing

File dau ra: `outputs/task42/` (11 file anh).

## 8. Day 4 — Task 4.3 (ROI & Perspective Transformation)
Chay demo:
```powershell
.venv\Scripts\python day4_task43.py [duong_dan_anh]
```
Neu khong co anh dau vao, chuong trinh tao anh mau `task43_synthetic.png` co mot nhan bi nghiêng (rotated rectangle) de minh hoa.

Noi dung:
- Tao anh mau nhan bi nghiêng + toa do 4 dinh.
- Crop ROI tu bounding box chua 4 dinh nhan.
- Perspective transform (`cv2.getPerspectiveTransform` + `cv2.warpPerspective`) chinh nhan nghiêng ve hinh chu nhat thang.
- Ghep truoc/sau de so sanh OCR input truoc va sau preprocessing.

File dau ra: `outputs/task43/` (roi_crop, perspective_corrected, before_after).

## 9. Unit tests (>= 12)
Tong 37 tests (12 Day 3 + 10 Task 4.1 + 8 Task 4.2 + 7 Task 4.3).

Ket qua moi lan chay: **37 passed** (0 warning).

**tests/test_scanner.py** (7): folder rong, anh hop le/hong, KHONG quet nested, invalid path, input khong phai thu muc, nhan dien duoi anh, checked_details.

**tests/test_report.py** (5): dung schema, cau truc valid/error, tu tao output folder, ghi de file cu, tich hop scan->build->JSON.

**tests/test_task41.py** (10): tra ve ndarray, shape/dtype/ndim, truy cap pixel, truy cap ROI, crop, resize, transpose, BGR->RGB, BGR->Gray, luu va tai lai anh.

**tests/test_task42.py** (8): Grayscale, Gaussian Blur, Threshold binary, Threshold Otsu, Adaptive Threshold, Canny edge, Morphological operations, pipeline xuat it thap 3 file.

**tests/test_task43.py** (7): tao anh mau nhan bi nghiêng, doc anh, crop ROI, perspective transform output shape, ma tran bien doi hop le, giu nguyen kenh mau, ghep truoc/sau.

Lenh chay thong nhat (CI va local):
```powershell
$env:PYTHONPATH = "src"
.venv\Scripts\python -m pytest tests/ -v
```
Hoac chay unittest cho Day 3:
```powershell
.venv\Scripts\python -m unittest discover -v -s tests
```

Ket qua moi lan chay: **26 passed** (0 warning).

## 10. system_info.py (stdlib only, Day 3)
Xuat JSON: Python version, operating system, current working directory, CPU count, `APP_ENV`, thoi gian chay script.
```powershell
$env:APP_ENV = "dev"
.venv\Scripts\python system_info.py
```

## 11. Linux / CLI practice (Day 3)
Da thuc hanh cac lenh tuong duong tren PowerShell: `Get-Location` (pwd), `Get-ChildItem` (ls/dir), `New-Item -ItemType Directory` (mkdir), `Get-Process` (ps), `netstat -ano` (ports), `$env:NAME` (env), `python -m ...` (module). `system_info.py` minh hoa doc env `APP_ENV`.

## 12. CI (GitHub Actions)
Workflow `.github/workflows/tests.yml`: chay khi push/PR, `ubuntu-latest`, checkout, setup Python 3.12, cai `requirements.txt`, chay `python -m unittest discover -v -s tests` (voi `PYTHONPATH=src`).

## 13. Commit & push
```powershell
git add -A
git commit -m "Day 3 + Day 4 Task 4.1-4.2: package, CLI JSON, 26 tests, system_info, CV labs"
git push -u origin main
```
Xem ket qua CI: GitHub repo → tab **Actions** → workflow "Python tests".
