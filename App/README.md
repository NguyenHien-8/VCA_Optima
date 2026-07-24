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
- Droplet Auto Detect dùng baseline làm ràng buộc hình học: mask bỏ substrate/reflection, cắt contour tails có clearance thấp, kiểm tra hai baseline anchors làm contact hints và lấy mẫu liquid-cap arc đều theo arc length.
- Droplet Measure Point hỗ trợ drag-select bằng selection rectangle: point được chọn được render màu đen, menu chuột phải chỉ hiện `Delete` khi có selection hợp lệ, và xóa theo index đã chọn trước khi dựng lại overlay.
- Các `QMainWindow` phụ (File Editor và Droplet Analysis) giữ quan hệ sở hữu với cửa sổ gọi nhưng luôn mang cờ `Qt.Window`; vì vậy hệ điều hành quản lý minimize/maximize độc lập và không xếp các title bar thu nhỏ trong vùng client của ứng dụng. Analysis window dùng `WA_DeleteOnClose` để giải phóng instance đã đóng.
- OpenCV, NumPy, Matplotlib và các editor nặng chỉ được import khi feature tương ứng được mở.
- File text được ghi nguyên tử; SQLite dùng context manager; đường dẫn và tên tài nguyên được kiểm tra trước thao tác phá hủy.
- `CrashHandler` ghi rotating log, cài exception hook cho main/background thread và bật `faulthandler`.

## Data Flow

1. `main.py` cài crash handler, tạo Qt shell và lazy-load `MainViewModel`/`MainView`.
2. View phát sự kiện → ViewModel kiểm tra đầu vào → Model hoặc worker thực hiện nghiệp vụ.
3. Worker trả kết quả bằng signal về UI thread.
4. Capture/record thành công phát `media_created` → SideBar cập nhật ngay; `QFileSystemWatcher` vẫn đồng bộ thay đổi từ bên ngoài.
5. Media scan nền cập nhật cache và `ChildIndicatorPolicy`; khi người dùng mở node, danh sách cache được render ngay.
6. Trong Droplet Analysis, baseline coefficients/anchors + image đi qua worker → liquid-cap contour + contact endpoints → ellipse/circle fit → overlay và contact angles.
7. Trong chế độ Measure Point, click vùng trống thêm point, drag vùng trống tạo selection rectangle, chuột phải selection → `Delete` → rebuild overlay từ danh sách point còn lại.
8. Mở File Editor/Droplet Analysis → tạo owned top-level window (`parent` + `Qt.Window`) → minimize/maximize do window manager xử lý ngoài layout của MainView.
9. Khi đóng, editor chờ worker hoàn tất theo tín hiệu, sau đó giải phóng camera, serial, multimedia, Matplotlib và lưu session.
