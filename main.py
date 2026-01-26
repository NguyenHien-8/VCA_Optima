# File: Ver1.1/main.py
import sys
import os
from PyQt6.QtWidgets import QApplication

# 1. Thêm đường dẫn gốc vào sys.path để đảm bảo Python nhìn thấy App và Vision
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 2. Import MainWindow từ đường dẫn mới (App/Gui)
try:
    from App.Gui.MainWindow import MainWindow
except ImportError as e:
    print("LỖI IMPORT: Vui lòng kiểm tra xem bạn đã tạo file __init__.py trong thư mục App và App/Gui chưa?")
    print(f"Chi tiết lỗi: {e}")
    sys.exit(1)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()