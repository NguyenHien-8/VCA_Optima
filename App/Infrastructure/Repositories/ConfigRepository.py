# App/Infrastructure/Repositories/ConfigRepository.py
import sqlite3
import os
from contextlib import contextmanager
from typing import Optional, Dict, Any
from App.Infrastructure.Repositories.StoragePath import persistent_database_path

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
            legacy_path = os.path.join(
                project_root,
                "App",
                "Infrastructure",
                "Persistence",
                "ConfigStorage.db",
            )
            db_path = persistent_database_path(
                "ConfigStorage.db", legacy_path=legacy_path
            )
        
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Tạo bảng nếu chưa tồn tại."""
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_config (
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

    # --- Generic methods ---
    def set_config(self, key: str, value: Any):
        """Lưu một cặp key-value (value sẽ được chuyển thành string)."""
        if not isinstance(key, str) or not key:
            raise ValueError("Configuration key must be a non-empty string.")
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO app_config (key, value) VALUES (?, ?)",
                (key, str(value))
            )

    def get_config(self, key: str) -> Optional[str]:
        """Lấy giá trị của key (trả về None nếu không tồn tại)."""
        if not isinstance(key, str) or not key:
            return None
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT value FROM app_config WHERE key = ?", (key,)
            ).fetchone()
        return row[0] if row else None

    def delete_config(self, key: str):
        """Xóa một key khỏi database."""
        if not isinstance(key, str) or not key:
            return
        with self._get_connection() as conn:
            conn.execute("DELETE FROM app_config WHERE key = ?", (key,))

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
        values = (
            ("hardware_port", str(port)),
            ("hardware_baud", str(baud)),
            ("hardware_period", str(period)),
        )
        with self._get_connection() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO app_config (key, value) VALUES (?, ?)",
                values,
            )

    def load_hardware_config(self) -> Dict[str, Any]:
        """Đọc cấu hình hardware, trả về dict với các key 'port', 'baud', 'period'."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT key, value FROM app_config "
                "WHERE key IN ('hardware_port', 'hardware_baud', 'hardware_period')"
            ).fetchall()
        values = dict(rows)
        port = values.get("hardware_port") or ""
        baud_str = values.get("hardware_baud")
        period_str = values.get("hardware_period")
        try:
            baud = int(baud_str) if baud_str is not None else 115200
            if baud <= 0:
                raise ValueError
        except (TypeError, ValueError):
            baud = 115200
        try:
            period = int(period_str) if period_str is not None else 100
            if period <= 0:
                raise ValueError
        except (TypeError, ValueError):
            period = 100
        return {
            "port": port,
            "baud": baud,
            "period": period
        }

    def clear_hardware_config(self):
        """Xóa toàn bộ cấu hình hardware (khi disconnect)."""
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM app_config WHERE key IN "
                "('hardware_port', 'hardware_baud', 'hardware_period')"
            )
