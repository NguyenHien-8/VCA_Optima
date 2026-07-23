# App/Infrastructure/Repositories/SessionRepository.py
import sqlite3
import os
import json
from typing import Optional, Any

class SessionRepository:
    """
    Repository quản lý việc đọc/ghi dữ liệu phiên làm việc (session) vào database SQLite.
    Sử dụng bảng 'session' với cấu trúc key-value.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Khởi tạo repository. Nếu không truyền db_path, tự động xác định đường dẫn
        tới file SessionData.db trong thư mục Persistence.
        """
        if db_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
            db_path = os.path.join(project_root, "App", "Infrastructure", "Persistence", "SessionData.db")

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Tạo bảng session nếu chưa tồn tại."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _get_connection(self):
        """Trả về kết nối database (dùng trong nội bộ)."""
        return sqlite3.connect(self.db_path)

    def save_session(self, key: str, value: Any):
        """
        Lưu một cặp key-value vào bảng session.
        value sẽ được chuyển thành chuỗi JSON.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO session (key, value) VALUES (?, ?)",
            (key, json.dumps(value))
        )
        conn.commit()
        conn.close()

    def load_session(self, key: str) -> Optional[Any]:
        """
        Đọc giá trị của key từ bảng session.
        Trả về dữ liệu đã được giải mã JSON, hoặc None nếu không tồn tại.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM session WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        if row:
            try:
                return json.loads(row[0])
            except (json.JSONDecodeError, TypeError):
                return None
        return None