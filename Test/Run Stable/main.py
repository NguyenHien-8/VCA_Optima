import sys
import os
from PyQt6.QtWidgets import QApplication

# --- CẤU HÌNH ĐƯỜNG DẪN IMPORT ---
# File này đang ở: Ver1.1/Src/main.py

# 1. Lấy đường dẫn thư mục hiện tại (Src)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Lấy đường dẫn thư mục gốc dự án (Ver1.1)
root_dir = os.path.dirname(current_dir)

# 3. Thêm root_dir vào sys.path để Python nhìn thấy package 'Src'
if root_dir not in sys.path:
    sys.path.append(root_dir)
# ---------------------------------

# QUAN TRỌNG: Phải dùng 'Src' (viết hoa) giống tên thư mục thực tế
from Src.Interfaces.MainWindow import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()