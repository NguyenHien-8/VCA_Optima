# App / Infrastructure

## Project Overview

Tầng hạ tầng cung cấp persistence, định vị tài nguyên và xử lý lỗi dùng chung. Tầng này không chứa logic UI hoặc nghiệp vụ project.

## Annotated Directory Structure

- `CrashHandler.py` — rotating log, Python/thread exception hook và native fault log.
- `Helpers/ResourceHelper.py` — giải quyết đường dẫn icon, QSS và asset trong source/PyInstaller.
- `Repositories/` — Config/Session SQLite repositories và `StoragePath`.
- `Persistence/` — vị trí database legacy dùng cho migration.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Log được ghi trong Local App Data và tự xoay vòng để giới hạn dung lượng.
- Database runtime đặt ở thư mục người dùng có quyền ghi; dữ liệu legacy được copy một lần nếu cần.
- SQLite connection luôn commit/rollback/close qua context manager.
- Lỗi logging hoặc migration không được phép ngăn ứng dụng khởi động.

## Data Flow

1. `main.py` cài `CrashHandler` trước khi import PyQt shell.
2. Repository yêu cầu đường dẫn từ `StoragePath`, mở transaction ngắn và đóng connection ngay.
3. ViewModel/Model đọc ghi cấu hình hoặc session qua repository.
4. Exception chưa xử lý được ghi log và hiển thị thông báo an toàn trên main thread.
