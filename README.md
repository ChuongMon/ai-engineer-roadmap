# Image Inspector (Day 3) — Package + CLI + Tests

## 1. Gioi thieu
Project da duoc refactor thanh package Python `image_inspector`.
- Quet anh trong **mot thu muc** (chi truc tiep, khong doc thu muc con) bang Pillow.
- Phan loai anh hop le / anh bi loi / file khong phai anh.
- Xuat bao cao **JSON** qua CLI.

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
│   ├── test_scanner.py     # 7 tests
│   └── test_report.py      # 5 tests
├── reports/                # thu muc output (file sinh ra bi .gitignore bo qua)
├── pyproject.toml
├── requirements.txt        # Pillow
├── system_info.py          # xuat thong tin he thong JSON (stdlib only)
├── README.md
├── .gitignore
├── .github/workflows/tests.yml
└── bao_cao_anh.py, test_bao_cao_anh.py  # phien ban cu (giu de tham chieu)
```

## 3. Yeu cau he thong
- Python >= 3.10 (CI dung 3.12)
- Pillow (`requirements.txt`)

## 4. Cai dat
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
(Linux/macOS: `source .venv/bin/activate` va `python3 -m pip install -r requirements.txt`)

## 5. Chay CLI (package)
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

## 6. Schema JSON bao cao
`build_report()`/CLI xuat JSON gom: `report_type`, `created_at`, `input_folder`, `method`, `summary` (`total_files`, `image_files`, `valid_images`, `error_images`, `non_image_files`), `valid_images`, `error_images` (co `file`, `ok`, `reason`), `non_image_files`.

## 7. Unit tests (>= 12)
Co 12 tests trong `tests/` (7 scanner + 5 report):

**tests/test_scanner.py**
1. `test_scan_folder_voi_folder_rong` — folder rong → total 0, danh sach rong.
2. `test_scan_folder_chua_anh_hop_le_va_anh_hong` — phan loai dung anh hop le/hong.
3. `test_scan_folder_khong_scan_thu_muc_con` — KHONG quet nested folders.
4. `test_scan_folder_invalid_input_path` — path khong ton tai → `FileNotFoundError`.
5. `test_scan_folder_input_khong_phai_thu_muc` — path la file → `NotADirectoryError`.
6. `test_is_image_file_nhan_dien_duoi` — nhan dien duoi anh (ke ca chu hoa).
7. `test_read_image_tra_ve_checked_details` — tra ve checked_details.

**tests/test_report.py**
8. `test_build_report_co_dung_schema` — JSON co dung schema/summary keys.
9. `test_build_report_valid_va_error_co_dung_cau_truc` — cau truc valid/error.
10. `test_write_report_tu_tao_output_folder` — tu tao thu muc output.
11. `test_write_report_ghi_de_file_cu` — overwrite file cu.
12. `test_report_tich_hop_scan_folder` — tich hop scan -> build -> JSON dung.

Lenh chay thong nhat (CI va local):
```powershell
$env:PYTHONPATH = "src"
.venv\Scripts\python -m unittest discover -v -s tests
```

## 8. system_info.py (stdlib only)
Xuat JSON: Python version, operating system, current working directory, CPU count, `APP_ENV`, thoi gian chay script.
```powershell
$env:APP_ENV = "dev"
.venv\Scripts\python system_info.py
```

## 9. Linux / CLI practice (Day 3)
Da thuc hanh cac lenh tuong duong tren PowerShell: `Get-Location` (pwd), `Get-ChildItem` (ls/dir), `New-Item -ItemType Directory` (mkdir), `Get-Process` (ps), `netstat -ano` (ports), `$env:NAME` (env), `python -m ...` (module). `system_info.py` minh hoa doc env `APP_ENV`.

## 10. CI (GitHub Actions)
Workflow `.github/workflows/tests.yml`: chay khi push/PR, `ubuntu-latest`, checkout, setup Python 3.12, cai `requirements.txt`, chay `python -m unittest discover -v -s tests` (voi `PYTHONPATH=src`).

## 11. Commit & push
```powershell
git add src tests pyproject.toml system_info.py README.md .gitignore .github/workflows/tests.yml requirements.txt reports/.gitignore reports/.gitkeep
git commit -m "Day 3: package refactor image_inspector, CLI JSON, 12 tests, system_info"
git push -u origin main
```
Xem ket qua CI: GitHub repo → tab **Actions** → workflow "Python tests".
