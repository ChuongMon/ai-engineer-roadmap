# Bao Cao Anh - Unit Test & Huong Dan Su Dung (v2)

## 1. Gioi thieu
Chuong trinh doc tat ca anh trong **mot thu muc** (chi truc tiep, khong doc thu muc con) bang Pillow,
phan biet anh hop le va anh bi loi, sau do xuat bao cao ra file notepad.

## 2. Yeu cau he thong
- Python 3.10+
- Thu vien Pillow (`PIL`) - khai bao trong `requirements.txt`

## 3. Cai dat moi truong (tai workspace)
Tai truong hop nay da co env san tai:
```
D:\Học Tập\Lộ trình 6 tháng AI\Level 0 — Engineering Foundation\Homework1\.venv
```

Kich hoat env va cai dat thu vien:
```powershell
# Tai thu muc Homework1
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Neu muon tao env moi:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 4. Chay chuong trinh (CLI bang argparse)
```powershell
.venv\Scripts\python bao_cao_anh.py --input "D:\DuLieu\Anh"
```

Hoặc chỉ định tên file báo cáo đầu ra:
```powershell
.venv\Scripts\python bao_cao_anh.py --input "D:\DuLieu\Anh" --output "bao_cao_anh.txt"
```

Tham số:
- `--input` (bat buoc): duong dan thu muc chua anh.
- `--output` (tuc chon, mac dinh `bao_cao_anh.txt`): ten file notepad xuat ket qua.

Ví dụ trên Windows:
```powershell
.venv\Scripts\python bao_cao_anh.py --input "D:\Học Tập\Lộ trình 6 tháng AI\Level 0 — Engineering Foundation\Homework1\test_anh"
```

Ket qua duoc luu vao:
```
D:\DuLieu\Anh\bao_cao_anh.txt
```

Xem huong dan su dung ngan gan:
```powershell
.venv\Scripts\python bao_cao_anh.py --help
```

## 5. Luat nghiep vu
- Chi doc file co duoi anh o **TRUC TIEP** trong thu muc nhap vao.
- KHONG doc trong cac thu muc con.
- File khong phai anh (duoi khong thuoc danh sach) se bo qua, KHONG tinh loi.
- Anh khong doc duoc boi Pillow se danh dau la [LOI] trong bao cao.
- Bao cao xuat ra file notepad (UTF-8).
- Neu chay lai, file bao cao cu se bi xoa hoan toan va tao file moi giong ten.

## 6. Cau truc bao cao notepad
Mot file `bao_cao_anh.txt` gom:
- Thoi gian tao, thu muc dau vao, file xuat.
- Phuong phap kiem tra: mo file bang `Image.open()` + `verify()`.
- Tong ket: tong so file, so anh, so anh khong loi, so anh bi loi, so file khong phai anh.
- Danh sach ANH KHONG LOI: ten file, ket qua, duoc kiem tra gi.
- Danh sach ANH BI LOI: ten file, ly do chi tiet, cach tai hien.
- Danh sach FILE KHONG PHAI ANH: bo qua, khong tinh loi.

## 7. Chay unit test
Co 7 unit test trong file `test_bao_cao_anh.py`:
1. `is_image_file` chap nhan duoi anh hop le.
2. `is_image_file` tu choi duoi khong phai anh.
3. `read_image` tra ve ok=True voi anh hop le.
4. `read_image` tra ve ok=False voi anh hong.
5. `scan_folder` dem dung so luong.
6. `scan_folder` khong doc thu muc con.
7. `build_report` chua cac phan khoa.

Lenh chay thong nhat (trong CI va local):
```powershell
.venv\Scripts\python -m unittest discover -v
```

## 8. Cau truc file
```
Homework1/
├── bao_cao_anh.py        # Chuong trinh chinh (argparse + pathlib)
├── test_bao_cao_anh.py   # Unit test (unittest)
├── requirements.txt      # Dependency: Pillow
├── README.md             # Huong dan su dung
├── .gitignore            # Bo loc .venv, __pycache__, *.txt (bao cao), ...
└── .github/workflows/tests.yml  # CI: push + PR, ubuntu-latest, Python 3.12
```

## 9. Commit code len Github

### Buoc 1: Kiem tra trang thai
```powershell
git status
```

### Buoc 2: Them file can dong bo (BO QUA .venv va bao cao sinh ra)
```powershell
git add bao_cao_anh.py test_bao_cao_anh.py requirements.txt README.md .gitignore .github/
```

### Buoc 3: Commit
```powershell
git commit -m "Refactor v2: argparse, pathlib, tach scan_folder/build_report, them unit test va CI"
```

### Buoc 4: Tao repository tren Github
- Dang nhap https://github.com
- Nhap "New repository", dat ten (vd: `bao-cao-anh`), KHOI TAO README (vi da co local).

### Buoc 5: Len lien ket local voi Github va push
```powershell
git remote add origin https://github.com/<ten-ban>/<ten-repo>.git
git branch -M main
git push -u origin main
```

### Buoc 6: Xem ket quả CI
- Sau khi push, o repository Github, nhap tab "Actions".
- Xem workflow "Python tests" chay lan dau.
- Ket quả xanh/do o o day.

## 10. Loi khuyen nghiep vien
- Tat ca duong dan su dung `pathlib.Path` de ho tro Windows, Linux, Mac.
- CLI dung `argparse` co `--input` va `--output`.
- Tach ham `scan_folder()` (quet thu muc) va `build_report()` (xay dung noi dung bao cao) de de unit test va bao tri.
- Khong su dung logging file; chi in thong bao ra CLI va luu bao cao notepad.
- Tat ca file bao cao sinh ra duoc bo trong `.gitignore` (`*.txt`).
