# App

## Project Overview

Package production của VCA Optima. Thư mục này gom toàn bộ mã ứng dụng và giữ ranh giới giữa giao diện, nghiệp vụ, hạ tầng và tài nguyên đóng gói.

## Annotated Directory Structure

- `Presentation/` — Views và ViewModels PyQt6.
- `Models/` — quản lý project/session, camera, media, serial và phân tích giọt.
- `Infrastructure/` — repositories SQLite và helper đường dẫn tài nguyên.
- `ReSource/` — QSS, SVG, ICO và splash screen.
- `__init__.py` — đánh dấu `App` là Python package.

## Core Algorithms & Implementation

- Kiến trúc gần MVVM: View chỉ hiển thị/thu sự kiện; ViewModel điều phối signal và manager; Model thực hiện nghiệp vụ; Repository cô lập SQLite.
- Các tác vụ blocking được tách khỏi UI bằng `QThread` cho camera, ghi video và thao tác file.
- Đường dẫn tài nguyên được giải quyết thống nhất cho cả source tree và bundle PyInstaller.

## Data Flow

1. `main.py` import `MainViewModel` và `MainView` từ package này.
2. `MainViewModel` khởi tạo manager/repository rồi phát signal cho `MainView`.
3. Views nhận dữ liệu đã xử lý, còn Models ghi filesystem, SQLite hoặc thiết bị ngoại vi.

