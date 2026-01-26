import sys
import os
import traceback # Thư viện để in chi tiết lỗi

# --- CẤU HÌNH ĐƯỜNG DẪN ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__)) # Thư mục Src
    root_dir = os.path.dirname(current_dir) # Thư mục Ver1.1
    
    # Thêm đường dẫn gốc vào sys.path để Python hiểu 'Src' là package
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir) # Dùng insert để ưu tiên đường dẫn này
    
    print(f"[DEBUG] Root Dir: {root_dir}")
    print(f"[DEBUG] Current Dir: {current_dir}")
except Exception as e:
    print(f"[CRITICAL] Lỗi cấu hình đường dẫn: {e}")
    input("Nhấn Enter để thoát...")
    sys.exit(1)

# --- IMPORT MODULE ---
try:
    print("[DEBUG] Đang import thư viện...")
    from PyQt6.QtWidgets import QApplication
    # Import class chính
    from Src.Interfaces.MainWindow import MainWindow
    print("[DEBUG] Import thành công!")
except ImportError as e:
    print("\n" + "="*30)
    print("[LỖI IMPORT] Python không tìm thấy file!")
    print("Gợi ý: Hãy kiểm tra xem trong các thư mục 'Src', 'Interfaces', 'Services' đã có file __init__.py chưa?")
    print(f"Chi tiết lỗi: {e}")
    print("="*30 + "\n")
    print(traceback.format_exc())
    input("Nhấn Enter để thoát...")
    sys.exit(1)

# --- HÀM MAIN ---
def main():
    try:
        print("[DEBUG] Khởi tạo QApplication...")
        app = QApplication(sys.argv)
        
        print("[DEBUG] Khởi tạo MainWindow...")
        window = MainWindow()
        
        print("[DEBUG] Đang hiển thị Window...")
        window.show()
        
        print("[DEBUG] Chương trình đang chạy...")
        exit_code = app.exec()
        sys.exit(exit_code)

    except Exception as e:
        print("\n" + "="*30)
        print("[LỖI RUNTIME] Chương trình bị crash!")
        print(f"Lỗi: {e}")
        print("="*30 + "\n")
        print(traceback.format_exc())
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()