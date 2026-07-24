# App

## Project Overview

`App` là package chính của VCA Optima Release 1.1.0. Mã nguồn được tổ chức theo hướng MVVM: giao diện PyQt6 ở `Presentation`, nghiệp vụ và thiết bị ở `Models`, lưu trữ và xử lý lỗi ở `Infrastructure`, còn tài nguyên đóng gói nằm trong `ReSource`.

Ứng dụng ưu tiên UI responsive: I/O, camera, serial, ghi media và phân tích ảnh chạy ngoài UI thread; các feature nặng được lazy import sau khi cửa sổ chính đã hiển thị.

## Annotated Directory Structure

- `Presentation/` — Views, ViewModels, worker và signal/slot điều phối UI.
- `Models/` — project/session, camera, serial, media và thuật toán phân tích giọt.
- `Infrastructure/` — SQLite repositories, đường dẫn dữ liệu, resource helper và crash handler.
- `ReSource/` — QSS, SVG, ICO và splash screen.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- `FunctionWorker`, các worker chuyên biệt và Qt queued signals đưa tác vụ blocking ra khỏi UI thread.
- Camera, recorder, filesystem scanner và editor sử dụng cooperative shutdown; `finished` kết hợp `deleteLater()` để giải phóng đúng vòng đời.
- SideBar dò nội dung `Image/Video` bằng hàng đợi scanner nền giới hạn đồng thời; branch indicator phản ánh nội dung thật mà không cần click để kích hoạt lazy load.
- OpenCV, NumPy, Matplotlib và các editor nặng chỉ được import khi feature tương ứng được mở.
- File text được ghi nguyên tử; SQLite dùng context manager; đường dẫn và tên tài nguyên được kiểm tra trước thao tác phá hủy.
- `CrashHandler` ghi rotating log, cài exception hook cho main/background thread và bật `faulthandler`.

## Data Flow

1. `main.py` cài crash handler, tạo Qt shell và lazy-load `MainViewModel`/`MainView`.
2. View phát sự kiện → ViewModel kiểm tra đầu vào → Model hoặc worker thực hiện nghiệp vụ.
3. Worker trả kết quả bằng signal về UI thread.
4. Capture/record thành công phát `media_created` → SideBar cập nhật ngay; `QFileSystemWatcher` vẫn đồng bộ thay đổi từ bên ngoài.
5. Media scan nền cập nhật cache và `ChildIndicatorPolicy`; khi người dùng mở node, danh sách cache được render ngay.
6. Khi đóng, editor chờ worker hoàn tất theo tín hiệu, sau đó giải phóng camera, serial, multimedia, Matplotlib và lưu session.
