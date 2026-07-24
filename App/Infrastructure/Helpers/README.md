# App / Infrastructure / Helpers

## Project Overview

Tiện ích dùng chung để xác định vị trí tài nguyên và chuẩn hóa ownership/taskbar cho cửa sổ phụ.

## Annotated Directory Structure

- `ResourceHelper.py` — xác định project/bundle root, tạo đường dẫn resource và nạp QSS tập trung.
- `WindowOwnershipHelper.py` — định danh taskbar, resolve logical owner và đăng ký secondary window với MainView.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- `base_path()` được cache, kiểm tra `sys.frozen`/`sys._MEIPASS`; khi chạy source, đi từ helper lên đúng project root mà không phụ thuộc current working directory.
- `resource_path()`, `app_resource_path()`, `icon_path()` và `stylesheet_path()` tạo đường dẫn tuyệt đối theo ngữ nghĩa.
- `load_stylesheet()` cache nội dung từng QSS; `apply_stylesheet()` áp dụng thống nhất cho widget và tránh đọc file lặp lại.
- `initialize_taskbar_identity()` đặt AppUserModelID trước khi tạo UI đầu tiên để MainView, File Editor và Droplet Analysis dùng cùng taskbar group.
- `configure_secondary_window()` tạo native handle trước lần show đầu, đăng ký window với MainView và áp dụng idempotent `WS_EX_APPWINDOW`/loại `WS_EX_TOOLWINDOW` trên Windows; không gán transient parent để từng window giữ trạng thái minimize độc lập.
- API Win32 được bọc defensive: validate handle, kiểm tra HRESULT/last-error, log lỗi và fallback an toàn; nền tảng khác vẫn dùng cơ chế đăng ký/điều phối của MainView.

## Data Flow

1. View yêu cầu đường dẫn QSS/icon.
2. Helper chọn project root hoặc `_MEIPASS`, sau đó nạp QSS/icon từ `App/ReSource`.
3. View mở file/tạo `QIcon` từ đường dẫn đã chuẩn hóa.
4. Secondary window resolve MainView logical owner → đăng ký để phối hợp minimize → bật grouped taskbar thumbnail → reapply idempotently trong `showEvent`.
