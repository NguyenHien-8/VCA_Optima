# App / Infrastructure

## Project Overview

Tầng hạ tầng cung cấp persistence, định vị tài nguyên và xử lý lỗi dùng chung. Tầng này không chứa logic UI hoặc nghiệp vụ project.

## Annotated Directory Structure

- `CrashHandler.py` — rotating log, Python/thread exception hook và native fault log.
- `Helpers/ResourceHelper.py` — giải quyết đường dẫn icon, QSS và asset trong source/PyInstaller.
- `Helpers/WindowOwnershipHelper.py` — AppUserModelID, logical-owner registration và Win32 taskbar style cho secondary windows.
- `Repositories/` — Config/Session SQLite repositories và `StoragePath`.
- `Persistence/` — vị trí database legacy dùng cho migration.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Log được ghi trong Local App Data và tự xoay vòng để giới hạn dung lượng.
- Database runtime đặt ở thư mục người dùng có quyền ghi; dữ liệu legacy được copy một lần nếu cần.
- SQLite connection luôn commit/rollback/close qua context manager.
- Lỗi logging hoặc migration không được phép ngăn ứng dụng khởi động.
- Window helper là no-op ngoài Windows; mọi lỗi Shell/User32 được log và fallback về hành vi Qt mặc định thay vì làm crash ứng dụng.

## Data Flow

1. `main.py` cài `CrashHandler` trước khi import PyQt shell.
2. Repository yêu cầu đường dẫn từ `StoragePath`, mở transaction ngắn và đóng connection ngay.
3. ViewModel/Model đọc ghi cấu hình hoặc session qua repository.
4. Exception chưa xử lý được ghi log và hiển thị thông báo an toàn trên main thread.
5. Startup đặt taskbar identity trước UI đầu tiên; secondary window tạo native handle, gán owner và taskbar style trước khi show.
