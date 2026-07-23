# App/Infrastructure/Repositories/SessionRepository.py
import sqlite3
import os
import json
from contextlib import contextmanager
from typing import Optional, Any
from App.Infrastructure.Repositories.StoragePath import persistent_database_path

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
            legacy_path = os.path.join(
                project_root,
                "App",
                "Infrastructure",
                "Persistence",
                "SessionData.db",
            )
            db_path = persistent_database_path(
                "SessionData.db", legacy_path=legacy_path
            )

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Tạo bảng session nếu chưa tồn tại."""
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

    @contextmanager
    def _get_connection(self):
        """Trả về kết nối database (dùng trong nội bộ)."""
        connection = sqlite3.connect(self.db_path, timeout=5.0)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def save_session(self, key: str, value: Any):
        """
        Lưu một cặp key-value vào bảng session.
        value sẽ được chuyển thành chuỗi JSON.
        """
        if not isinstance(key, str) or not key:
            raise ValueError("Session key must be a non-empty string.")
        payload = json.dumps(value, ensure_ascii=False)
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO session (key, value) VALUES (?, ?)",
                (key, payload)
            )

    def load_session(self, key: str) -> Optional[Any]:
        """
        Đọc giá trị của key từ bảng session.
        Trả về dữ liệu đã được giải mã JSON, hoặc None nếu không tồn tại.
        """
        if not isinstance(key, str) or not key:
            return None
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT value FROM session WHERE key = ?", (key,)
            ).fetchone()
        if row:
            try:
                return json.loads(row[0])
            except (json.JSONDecodeError, TypeError):
                return None
        return None
