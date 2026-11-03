# Bao Cao Anh - Unit Test & Huong Dan Su Dung

## 1. Gioi thieu
Chuong trinh doc tat ca anh trong **mot thu muc** (khong doc thu muc con) bang Pillow,
phan biet anh hop le va anh bi loi, sau do xuat bao cao ra file notepad
`bao_cao_anh.txt` o cung thu muc dau vao.

## 2. Yeu cau he thong
- Python 3.10+
- Thu vien Pillow (`PIL`)

## 3. Cai dat moi truong (tai workspace)
Tai truong hop nay da tao san env tai:
```
D:\Học Tập\Lộ trình 6 tháng AI\Level 0 — Engineering Foundation\Homework1\.venv
```

Kich hoat env va cai dat thu vien:
```powershell
# Tai thu muc Homework1
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install Pillow
```

Neu muon tao env moi:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install Pillow
```

## 4. Chay chuong trinh
```powershell
.venv\Scripts\python bao_cao_anh.py
```

Sau khi chay, nhap duong dan thu muc chua anh khi yeu cau.
Ví dụ:
```
Nhap duong dan thu muc chua anh: D:\DuLieu\Anh
```

Ket qua se duoc luu vao:
```
D:\DuLieu\Anh\bao_cao_anh.txt
```

## 5. Luat nghiep vu
- Chi doc file co duoi anh o **TRUC TIEP** trong thu muc nhap vao.
- KHONG doc trong cac thu muc con.
- File khong phai anh (duoi khong thuoc danh sach) se bo qua, KHONG tinh loi.
- Anh khong doc duoc boi Pillow se danh dau la [LOI] trong bao cao.
- Bao cao xuat ra file notepad `bao_cao_anh.txt` (UTF-8).
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
Co 3 unit test trong file `test_bao_cao_anh.py`:

```powershell
.venv\Scripts\python -m unittest test_bao_cao_anh.py -v
```

Cac test cover:
1. `is_image_file` chap nhan duoi anh hop le.
2. `is_image_file` tu choi duoi khong phai anh.
3. `read_image` tra ve ok=True voi anh hop le.
4. `read_image` tra ve ok=False voi anh hong.

## 8. Cau truc file
```
Homework1/
├── bao_cao_anh.py        # Chuong trinh chinh
├── test_bao_cao_anh.py   # 3 unit test (unittest)
├── README.md             # Huong dan su dung
├── .venv/                # Moi truong Python (khong commit)
├── .gitignore            # Bo loc file khong commit
└── test_anh/             # Thu muc du lieu test (khong commit)
```

## 9. Loi khuyen nghiep vien
- Tat ca xuat ra notepad duoc ma hoa UTF-8 de ho tro tieng Viet.
- Khong su dung logging file; chi in thong bao ra CLI va luu bao cao notepad.
- Chay lai script se xoa toan bo noi dung bao cu va tao notepad moi giong ten.
