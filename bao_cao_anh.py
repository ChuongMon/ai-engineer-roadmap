from PIL import Image, UnidentifiedImageError
import os
import sys
from datetime import datetime

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif",
    ".webp", ".ico", ".ppm", ".pgm", ".pbm", ".pcx", ".xbm",
}

OUTPUT_FILENAME = "bao_cao_anh.txt"


def is_image_file(filename):
    _, ext = os.path.splitext(filename)
    return ext.lower() in IMAGE_EXTENSIONS


def read_image(filepath):
    """Tra ve (ok: bool, error: str|None, checked: str)"""
    checked = "Mo file bang Pillow (Image.open) + verify() de xac thuc du lieu anh."
    try:
        with Image.open(filepath) as img:
            img.verify()
        return True, None, checked
    except UnidentifiedImageError as e:
        reason = "Khong nhan duoc dinh dang anh (UnidentifiedImageError): " + str(e)
        repro = "Cach tai hien: Chay 'Image.open(r\"' + filepath + '\")' -> PIL khong nhan dinh dang file."
        return False, reason + " | " + repro, checked
    except OSError as e:
        reason = "Loi doc anh (OSError): " + str(e)
        repro = "Cach tai hien: Chay 'Image.open(r\"' + filepath + '\")' -> OSError khi doc file."
        return False, reason + " | " + repro, checked
    except Exception as e:
        reason = "Loi khong xac dinh: " + str(e)
        repro = "Cach tai hien: Chay 'Image.open(r\"' + filepath + '\")' -> Ngoai le khong xac dinh."
        return False, reason + " | " + repro, checked


def build_report(input_folder, valid_images, error_images, non_image_files, total_files, checked_details):
    lines = []
    lines.append("=" * 60)
    lines.append("BAO CAO THONG KE ANH")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Thoi gian tao: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    lines.append("Thu dau vao: " + input_folder)
    lines.append("File xuat: " + OUTPUT_FILENAME)
    lines.append("")
    lines.append("-" * 60)
    lines.append("PHUONG PHAP KIEM TRA (duoc ap dung voi tat ca file co duoi anh)")
    lines.append("-" * 60)
    if checked_details:
        lines.append("  " + checked_details)
    else:
        lines.append("  (Khong co file anh nao duoc kiem tra)")
    lines.append("")
    lines.append("-" * 60)
    lines.append("TONG KET")
    lines.append("-" * 60)
    lines.append("Tong so file trong thu muc: " + str(total_files))
    lines.append("So file la anh (co duoi anh): " + str(len(valid_images) + len(error_images)))
    lines.append("Anh doc duoc (khong loi): " + str(len(valid_images)))
    lines.append("Anh bi loi (khong doc duoc): " + str(len(error_images)))
    lines.append("File khong phai anh (bo qua, khong loi): " + str(len(non_image_files)))
    lines.append("")
    lines.append("-" * 60)
    lines.append("DANH SACH ANH KHONG LOI (" + str(len(valid_images)) + ")")
    lines.append("-" * 60)
    if valid_images:
        for name in valid_images:
            lines.append("  [OK] " + name)
            lines.append("       File: " + name)
            lines.append("       Ket qua: Khong loi - doc thanh cong bang Pillow.")
            lines.append("       Duoc kiem tra: Mo file bang Image.open() + verify(), khong ngoai le.")
    else:
        lines.append("  (Khong co)")
    lines.append("")
    lines.append("-" * 60)
    lines.append("DANH SACH ANH BI LOI (" + str(len(error_images)) + ")")
    lines.append("-" * 60)
    if error_images:
        for item in error_images:
            name = item[0]
            detail = item[1]
            lines.append("  [LOI] " + name)
            lines.append("       File: " + name)
            lines.append("       Ly do: " + detail)
    else:
        lines.append("  (Khong co)")
    lines.append("")
    lines.append("-" * 60)
    lines.append("DANH SACH FILE KHONG PHAI ANH (BO QUA, KHONG TINH LOI) (" + str(len(non_image_files)) + ")")
    lines.append("-" * 60)
    if non_image_files:
        for name in non_image_files:
            lines.append("  [BO QUA] " + name)
            lines.append("       File: " + name)
            lines.append("       Ly do: Duoi file khong thuoc danh sach dinh dang anh ho tro.")
    else:
        lines.append("  (Khong co)")
    lines.append("")
    lines.append("=" * 60)
    lines.append("KET THUC BAO CAO")
    lines.append("=" * 60)
    return "\n".join(lines) + "\n"


def safe_print(text):
    try:
        __builtins__.print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("cp1252", errors="replace") + b"\n")


def main():
    safe_print("=" * 60)
    safe_print("CHUONG TRINH THONG KE ANH THEO THU MUC")
    safe_print("=" * 60)
    safe_print("Chi doc anh o TRUC TIEP trong thu muc nhap vao.")
    safe_print("KHONG doc trong cac thu muc con.")
    safe_print("File khong phai anh se bo qua, KHONG tinh loi.")
    safe_print("Anh anh khong doc duoc se danh dau la LOI.")
    safe_print("Ket qua xuat ra file notepad: " + OUTPUT_FILENAME)
    safe_print("Neu chay lai, file cu se bi xoa hoan toan va tao file moi giong ten.")
    safe_print("=" * 60)
    safe_print("")

    while True:
        input_folder = input("Nhap duong dan thu muc chua anh: ").strip()
        if not input_folder:
            safe_print("Vui long nhap duong dan hop le.")
            continue
        input_folder = os.path.abspath(input_folder)
        if not os.path.isdir(input_folder):
            safe_print("Duong dan khong phai thu muc hoac khong ton tai: " + input_folder)
            continue
        break

    output_path = os.path.join(input_folder, OUTPUT_FILENAME)

    valid_images = []
    error_images = []
    non_image_files = []
    total_files = 0
    checked_details = None

    try:
        entries = list(os.scandir(input_folder))
    except PermissionError as e:
        safe_print("KHONG THE DOC THU MUC (qua trinh quyen): " + str(e))
        sys.exit(1)
    except OSError as e:
        safe_print("Loi khi mo thu muc: " + str(e))
        sys.exit(1)

    for entry in entries:
        if not entry.is_file():
            continue
        total_files += 1
        name = entry.name
        if not is_image_file(name):
            non_image_files.append(name)
            continue
        ok, reason, checked = read_image(entry.path)
        if checked_details is None:
            checked_details = checked
        if ok:
            valid_images.append(name)
        else:
            error_images.append((name, reason))

    report = build_report(input_folder, valid_images, error_images, non_image_files, total_files, checked_details)

    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except OSError as e:
            safe_print("Khong the xoa file cu: " + str(e))

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
    except OSError as e:
        safe_print("Loi ghi file bao cao: " + str(e))
        sys.exit(1)

    safe_print("")
    safe_print("=" * 60)
    safe_print("HOAN TAT!")
    safe_print("=" * 60)
    safe_print("Thu muc dau vao: " + input_folder)
    safe_print("File bao cao:    " + output_path)
    safe_print("Tong file:       " + str(total_files))
    safe_print("Anh khong loi:   " + str(len(valid_images)))
    safe_print("Anh bi loi:      " + str(len(error_images)))
    safe_print("File khong anh:  " + str(len(non_image_files)))
    safe_print("=" * 60)


if __name__ == "__main__":
    main()
