# App / Infrastructure / Persistence

## Project Overview

Kho lưu trữ SQLite được bundle cùng ứng dụng cho cấu hình thiết bị và trạng thái phiên làm việc.

## Annotated Directory Structure

- `ConfigStorage.db` — bảng `app_config(key TEXT PRIMARY KEY, value TEXT)`.
- `SessionData.db` — bảng `session(key TEXT PRIMARY KEY, value TEXT)`; có thể thay đổi trong lúc chạy.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Config lưu camera index, hardware port, baud và query period theo key riêng.
- Session lưu danh sách project/editor, expanded paths và opened items dưới dạng JSON.
- Database được tạo bảng tự động bởi repository khi thiếu; README không phải dữ liệu runtime.

## Data Flow

1. `ConfigRepository`/`SessionRepository` mở file tương ứng.
2. UI thay đổi trạng thái → manager/repository commit SQLite.
3. Lần khởi động sau đọc lại dữ liệu để phục hồi cấu hình/session.

