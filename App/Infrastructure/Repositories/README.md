# App / Infrastructure / Repositories

## Project Overview

Các repository cô lập SQLite khỏi ViewModel và cung cấp persistence key-value cho cấu hình ứng dụng cùng phiên làm việc.

## Annotated Directory Structure

- `ConfigRepository.py` — camera index và hardware configuration.
- `SessionRepository.py` — project, opened item/editor và expanded path dưới dạng JSON.
- `StoragePath.py` — đường dẫn database per-user và migration database legacy.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Mỗi thao tác dùng connection riêng với timeout hữu hạn.
- Context manager bảo đảm commit khi thành công, rollback khi lỗi và luôn đóng handle.
- Key rỗng bị từ chối; JSON được encode Unicode; giá trị số cấu hình có fallback an toàn.
- `save_hardware_config` ghi các trường liên quan trong một transaction.

## Data Flow

1. Repository xác định database trong Local App Data.
2. Nếu database mới chưa tồn tại, `StoragePath` thử migrate bản legacy.
3. ViewModel/SessionManager gọi API repository.
4. SQLite trả dữ liệu thuần; parsing và fallback diễn ra trước khi dữ liệu đi vào manager.
