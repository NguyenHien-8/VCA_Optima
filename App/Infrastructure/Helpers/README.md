# App / Infrastructure / Helpers

## Project Overview

Tiện ích dùng chung để xác định vị trí tài nguyên bất kể ứng dụng chạy từ source hay executable PyInstaller.

## Annotated Directory Structure

- `ResourceHelper.py` — xác định project/bundle root, tạo đường dẫn resource và nạp QSS tập trung.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- `base_path()` được cache, kiểm tra `sys.frozen`/`sys._MEIPASS`; khi chạy source, đi từ helper lên đúng project root mà không phụ thuộc current working directory.
- `resource_path()`, `app_resource_path()`, `icon_path()` và `stylesheet_path()` tạo đường dẫn tuyệt đối theo ngữ nghĩa.
- `load_stylesheet()` cache nội dung từng QSS; `apply_stylesheet()` áp dụng thống nhất cho widget và tránh đọc file lặp lại.

## Data Flow

1. View yêu cầu đường dẫn QSS/icon.
2. Helper chọn project root hoặc `_MEIPASS`, sau đó nạp QSS/icon từ `App/ReSource`.
3. View mở file/tạo `QIcon` từ đường dẫn đã chuẩn hóa.
