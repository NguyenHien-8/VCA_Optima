# App/Infrastructure/Repositories/ConfigRepository.py
import sqlite3
import os
from typing import Optional, Dict, Any

class ConfigRepository:
    """
    Repository quản lý việc đọc/ghi cấu hình ứng dụng vào database SQLite.
    Sử dụng bảng 'app_config' với cấu trúc key-value.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Khởi tạo repository. Nếu không truyền db_path, tự động xác định đường dẫn
        tới file ConfigStorage.db trong thư mục Persistence.
        """
        if db_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
            db_path = os.path.join(project_root, "App", "Infrastructure", "Persistence", "ConfigStorage.db")
        
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Tạo bảng nếu chưa tồn tại."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _get_connection(self):
        """Trả về kết nối database (dùng trong nội bộ)."""
        return sqlite3.connect(self.db_path)

    # --- Generic methods ---
    def set_config(self, key: str, value: Any):
        """Lưu một cặp key-value (value sẽ được chuyển thành string)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO app_config (key, value) VALUES (?, ?)",
            (key, str(value))
        )
        conn.commit()
        conn.close()

    def get_config(self, key: str) -> Optional[str]:
        """Lấy giá trị của key (trả về None nếu không tồn tại)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_config WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def delete_config(self, key: str):
        """Xóa một key khỏi database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM app_config WHERE key = ?", (key,))
        conn.commit()
        conn.close()

    # --- Camera config ---
    def save_camera_index(self, index: Optional[int]):
        """Lưu chỉ số camera đang dùng."""
        if index is None:
            self.delete_config("camera_index")
        else:
            self.set_config("camera_index", index)

    def load_camera_index(self) -> Optional[int]:
        """Đọc chỉ số camera, trả về None nếu chưa có."""
        val = self.get_config("camera_index")
        if val is not None:
            try:
                return int(val)
            except ValueError:
                return None
        return None

    # --- Hardware config ---
    def save_hardware_config(self, port: str, baud: int, period: int):
        """Lưu cấu hình hardware."""
        self.set_config("hardware_port", port)
        self.set_config("hardware_baud", baud)
        self.set_config("hardware_period", period)

    def load_hardware_config(self) -> Dict[str, Any]:
        """Đọc cấu hình hardware, trả về dict với các key 'port', 'baud', 'period'."""
        port = self.get_config("hardware_port") or ""
        baud_str = self.get_config("hardware_baud")
        period_str = self.get_config("hardware_period")
        baud = int(baud_str) if baud_str is not None else 115200
        period = int(period_str) if period_str is not None else 100
        return {
            "port": port,
            "baud": baud,
            "period": period
        }

    def clear_hardware_config(self):
        """Xóa toàn bộ cấu hình hardware (khi disconnect)."""
        self.delete_config("hardware_port")
        self.delete_config("hardware_baud")
        self.delete_config("hardware_period")