# App / Infrastructure

## Project Overview

Lớp hạ tầng chứa các adapter kỹ thuật mà nghiệp vụ phụ thuộc: tra cứu tài nguyên, repositories SQLite và các file database đi kèm.

## Annotated Directory Structure

- `Helpers/` — helper tìm resource path.
- `Repositories/` — API đọc/ghi config và session.
- `Persistence/` — `ConfigStorage.db` và `SessionData.db`.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Repository dùng câu lệnh tham số hóa và `INSERT OR REPLACE` để lưu key–value.
- Session serialize giá trị bằng JSON; config lưu chuỗi rồi ép kiểu ở API chuyên biệt.
- Model/View không cần biết SQL schema hoặc vị trí bundle.

## Data Flow

1. Manager gọi Repository.
2. Repository mở SQLite connection ngắn hạn, đọc/commit rồi đóng.
3. Helper trả absolute path cho View khi tải QSS/icon.

