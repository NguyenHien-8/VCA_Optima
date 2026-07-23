# App / Infrastructure / Repositories

## Project Overview

Lớp truy cập dữ liệu SQLite, cung cấp API nhỏ và có kiểu dữ liệu phù hợp cho phần Models.

## Annotated Directory Structure

- `ConfigRepository.py` — CRUD key–value và API camera/hardware.
- `SessionRepository.py` — JSON serialize/deserialize trạng thái phiên.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- `ConfigRepository` dùng `INSERT OR REPLACE`, ép camera index/baud/period về số và cung cấp giá trị mặc định.
- `SessionRepository` JSON-encode mọi giá trị; lỗi decode trả `None` thay vì làm hỏng luồng restore.
- Mỗi thao tác dùng connection riêng, commit khi ghi rồi đóng ngay.

## Data Flow

1. `MainViewModel` nạp config và tạo `SessionManager`.
2. Manager gọi repository bằng semantic key.
3. Repository đọc/ghi file trong `Persistence/` và trả object Python.

