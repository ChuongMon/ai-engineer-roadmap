# Image Inspector + Computer Vision Labs (Day 3–Day 5)

## 1. Gioi thieu
Project gom package Python `image_inspector` (Day 3), cac bai Computer Vision (Day 4) va Detection Evaluation Labs (Day 5).
- Quet anh trong **mot thu muc** (chi truc tiep, khong doc thu muc con) bang Pillow.
- Phan loai anh hop le / anh bi loi / file khong phai anh.
- Xuat bao cao **JSON** qua CLI.
- NumPy Image Fundamentals (Task 4.1): doc anh thanh array, shape/dtype/ndim, pixel & ROI, crop/resize/transpose, chuyen doi BGR/RGB/Grayscale, giai ly do OpenCV doc BGR.
- OpenCV Preprocessing (Task 4.2): Grayscale, Gaussian Blur, Thresholding (binary + Otsu), Adaptive Threshold, Canny edge, Morphological (Erosion, Dilation, Opening, Closing) tren cung mot anh.
- Detection fundamentals (Day 5): contours, axis-aligned/rotated boxes, IoU, hard NMS va Precision/Recall/F1 tren du lieu tong hop.

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
│   ├── test_task42.py      # Day 4 Task 4.2: preprocessing tests
│   ├── test_task51.py      # Day 5: contours / boxes
│   ├── test_task52.py      # Day 5: IoU
│   ├── test_task53.py      # Day 5: Hard NMS
│   └── test_task54.py      # Day 5: detection metrics
├── outputs/                # thu muc output sinh ra (bi .gitignore bo qua)
├── reports/                # thu muc output JSON Day 3 (bi .gitignore bo qua)
├── pyproject.toml
├── requirements.txt        # Pillow, numpy, opencv-python, matplotlib, pytest
├── system_info.py          # xuat thong tin he thong JSON (stdlib only)
├── day4_task41.py          # Day 4 Task 4.1 demo script
├── day4_task42.py          # Day 4 Task 4.2 demo script
├── day5_task51.py          # contours and bounding boxes
├── day5_task52.py          # IoU utilities
├── day5_task53.py          # Hard NMS + visualization
├── day5_task54.py          # TP/FP/FN, P/R/F1 + JSON report
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

## 9. Unit tests
Hien co 118 tests trong `tests/` (12 Day 3 + 12 Task 4.1 + 10 Task 4.2 + 13 Task 4.3 + 17 Task 5.1 + 23 Task 5.2 + 15 Task 5.3 + 16 Task 5.4), va 11 tests trong `computer_vision_labs/tests/` — tong cong **129 tests**.

Ket qua full suite gan nhat: **129 passed**. CI chay hai nhom test rieng, nhu cac lenh ben duoi.

**tests/test_scanner.py** (7): folder rong, anh hop le/hong, KHONG quet nested, invalid path, input khong phai thu muc, nhan dien duoi anh, checked_details.

**tests/test_report.py** (5): dung schema, cau truc valid/error, tu tao output folder, ghi de file cu, tich hop scan->build->JSON.

**tests/test_task41.py** (12): tra ve ndarray, shape/dtype/ndim, truy cap pixel/ROI, crop, resize, transpose, chuyen BGR->RGB/Gray, luu va tai lai anh, validate kich thuoc toi thieu.

**tests/test_task42.py** (10): Grayscale, Gaussian Blur, Threshold binary/Otsu, Adaptive Threshold, Canny edge, morphology tren Canny va binary, blur truoc threshold, pipeline tao output.

**tests/test_task43.py** (13): tao/doc anh mau, crop ROI, perspective transform (shape, matrix, channels, canh chinh), quadrilateral validation, ROI rong va quadrilateral xoay.

**tests/test_task51.py** (17): validate anh nhi phan, tim contour, loc theo dien tich, bounding box, minAreaRect/boxPoints, tao anh mau va tim du 5 contour.

**tests/test_task52.py** (23): IoU identity/disjoint/overlap/containment, hai box formats, box zero-area/toa do am/input sai, ma tran IoU, one-to-one matching va threshold.

**tests/test_task53.py** (15): hard NMS, overlap/no-overlap, threshold, tie-break, index goc, xywh, scores/inputs sai va demo output.

**tests/test_task54.py** (16): TP/FP/FN, Precision/Recall/F1, match theo score, duplicate detection, IoU threshold, input rong/sai va JSON report demo.

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

## 12. Computer Vision Labs (Day 4 Task 4.4 — Mini Project)
Thu muc `computer_vision_labs/` chua pipeline xu ly anh hoan chinh:

```
computer_vision_labs/
├── data/sample.png
├── src/loader.py, preprocessing.py, roi.py, main.py
├── outputs/ (7 file anh + before_after.png)
├── tests/test_pipeline.py (11 tests)
└── README.md
```

Chay:
```powershell
$env:PYTHONPATH = "computer_vision_labs/src"
.venv\Scripts\python computer_vision_labs/src/main.py --input computer_vision_labs/data/sample.png --output-dir computer_vision_labs/outputs --pts 150,100,450,120,420,280,120,260
```

Chay test:
```powershell
.venv\Scripts\python -m pytest computer_vision_labs/tests/ -v   # 11 passed
```

## 13. CI (GitHub Actions)
Workflow `.github/workflows/tests.yml`: chay khi push/PR, `ubuntu-latest`, checkout, setup Python 3.12, cai `requirements.txt`, chay `python -m unittest discover -v -s tests` (voi `PYTHONPATH=src`).

## 14. Day 5 — Task 5.1 (Contours và bounding boxes)

Chay demo:
```powershell
.venv\Scripts\python day5_task51.py
```
Khong can anh dau vao: chuong trinh tao anh mau `task51_synthetic.png` co 5 hinh chu nhat
(3 hinh thang, 1 hinh xoay, 1 vung nhieu nho).

Noi dung:
- Kiem tra anh dau vao phai la nhi phan 2D uint8 (chi gia tri 0 va 255).
- Tim contour ngoai bang `cv2.findContours` (RETR_EXTERNAL, CHAIN_APPROX_SIMPLE).
- Loc contour theo dien tich (`cv2.contourArea`).
- Tinh `boundingRect` (hinh chu nhat thang theo truc) va `minAreaRect` (hinh chu nhat nho nhat, co the xoay).
- Lay 4 dinh cua `minAreaRect` bang `cv2.boxPoints`.
- Ve contour, bounding box, minAreaRect len anh minh hoa va luu ket qua.

File dau ra: `outputs/task51/task51_contours_boxes.png` va `task51_synthetic.png`.

Gioi han can biet:
- `contourArea` tinh tu da giac cac diem contour, khong phai so pixel trang.
- Voi `RETR_EXTERNAL`, contour ben trong va khoang trong khong duoc tra nhu contour ngoai rieng.
- `minAreaRect` bao hinh chu nhat xoay trong mat phinh, KHONG chinh sua pho canh (mat thang thanh thang).
- Ngưỡng dien tich tuyet tuoi co nghia khac nhau theo kich thuoc anh; nen truyen ngưỡng ro rang.

Tests:
```powershell
$env:PYTHONPATH = "src"
.venv\Scripts\python -m pytest tests/test_task51.py -v
```

Phan nay chi tap trung contours; khong bao gom NMS, precision/recall, mAP hoac nhan dien nhan tren anh that. Day la bai de hieu hinh hoc co ban va gioi han cua contours.

## 15. Day 5 — Task 5.2 (Intersection over Union)

IoU so sanh muc do chong lan giua hai bounding box axis-aligned:
`IoU = intersection_area / union_area`. Hai box khong giao nhau co IoU 0;
box giong nhau co IoU 1. Bai nay khong ho tro rotated boxes.

Chay test:
```powershell
.venv\Scripts\python -m pytest tests/test_task52.py -v
```

`day5_task52.py` ho tro hai format, can chi ro `box_format`:
- `xyxy`: `(x1, y1, x2, y2)` (mac dinh).
- `xywh`: `(x, y, width, height)`.

Box co width/height bang 0 duoc chap nhan va co IoU 0; kich thuoc am,
toa do XYXY dao nguoc, gia tri khong huu han hoac box sai cau truc se bi tu choi.
`iou_matrix` tra ma tran `(so_predictions, so_ground_truths)`.
`match_boxes` chi ghep mot-mot, chon cap IoU cao nhat truoc (hoa thi theo index);
day la heuristic tham lam, khong dam bao toi uu toan cuc. `threshold` nam trong
`[0, 1]`, mac dinh `0.5`. Chua lam precision/recall hoac mAP.

## 16. Day 5 — Task 5.3 (Hard Non-Maximum Suppression)

NMS sap xep box theo score giam dan, giu box score cao nhat va loai box con lai
khi IoU voi box da giu **lon hon** threshold. Threshold thap hon thuong suppress
nhieu box hon. Score hoa thi uu tien index ban dau nho hon.

Chay demo va test:
```powershell
.venv\Scripts\python day5_task53.py
.venv\Scripts\python -m pytest tests/test_task53.py -v
```

`nms()` tra index goc theo thu tu score giam dan; `nms_with_scores()` tra cap
`(index, score)`. Ho tro format `xyxy` mac dinh va `xywh` qua `box_format`,
dung lai ham IoU cua Task 5.2. Score phai huu han va khong am; threshold nam
trong `[0, 1]`. Demo tong hop luu anh vao `outputs/task53/task53_nms.png`.
Phan Hard NMS nay khong gom Soft-NMS hoac rotated boxes.

## 17. Day 5 — Task 5.4 (Detection Evaluation)

Chay demo tao report JSON:
```powershell
.venv\Scripts\python day5_task54.py
.venv\Scripts\python -m pytest tests/test_task54.py -v
```
Chay tat ca tests cua Day 5:
```powershell
.venv\Scripts\python -m pytest tests/test_task51.py tests/test_task52.py tests/test_task53.py tests/test_task54.py -v
```

Demo dung box tong hop cho **mot anh, mot lop** va ghi
`outputs/task54/detection_report.json`, gom ground truth, predictions, ma tran
IoU, ket qua NMS va cac metrics:
- TP: prediction duoc ghep voi mot ground truth chua ghep tai IoU >= nguong.
- FP: prediction khong duoc ghep; detection trung lap cung la FP.
- FN: ground truth khong duoc prediction nao tim thay.
- Precision = TP/(TP+FP); Recall = TP/(TP+FN); F1 la trung binh dieu hoa
  Precision va Recall. Neu mau so bang 0, demo quy uoc metric tuong ung bang 0.

Precision tra loi "trong cac box da du doan, bao nhieu box dung?"; Recall tra loi
"trong cac vat the that, tim thay bao nhieu?". Tang nguong IoU lam tieu chuan
match chat hon; tang confidence threshold thuong giam FP nhung co the tang FN.

AP la dien tich/tong hop duoi duong Precision-Recall khi quet confidence
threshold. mAP la trung binh AP tren cac lop; mAP50 dung IoU 0.50, con mAP50-95
lay trung binh tai cac nguong IoU 0.50, 0.55, ..., 0.95. Day lab chi tinh
Precision/Recall/F1 tai mot nguong IoU cho mot anh/mot lop; **chua tinh AP/mAP**
va chua danh gia model tren tap anh that. Muon so sanh model, can dataset co
ground truth du dai dien va quy tac danh gia nhat quan.

## 13. Commit & push
```powershell
git add -A
git commit -m "Day 3 + Day 4 Task 4.1-4.2: package, CLI JSON, 26 tests, system_info, CV labs"
git push -u origin main
```
Xem ket qua CI: GitHub repo → tab **Actions** → workflow "Python tests".
