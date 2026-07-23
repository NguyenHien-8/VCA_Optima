# App / Infrastructure / Persistence

## Project Overview

Thư mục tương thích cho database SQLite legacy. Database đang chạy không còn được ghi cạnh source hoặc executable; repository sử dụng Local App Data của người dùng.

## Annotated Directory Structure

- `ConfigStorage.db` — dữ liệu cấu hình legacy, chỉ dùng làm nguồn migration nếu tồn tại.
- `SessionData.db` — dữ liệu session legacy, chỉ dùng làm nguồn migration nếu tồn tại.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- `StoragePath.persistent_database_path()` tạo thư mục dữ liệu per-user có quyền ghi.
- Khi target chưa tồn tại, file legacy được copy một lần; lỗi copy không ngăn startup.
- Schema và transaction vẫn do `ConfigRepository`/`SessionRepository` quản lý.
- Không thêm database runtime mới vào source tree.

## Data Flow

1. Repository yêu cầu đường dẫn database runtime.
2. `StoragePath` kiểm tra target trong Local App Data.
3. Nếu cần, dữ liệu legacy tại đây được migrate.
4. Mọi lần đọc/ghi sau đó diễn ra trên database per-user.
