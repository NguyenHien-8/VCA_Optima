# VCA Optima — Release 1.1.0

## Project Overview

VCA Optima là ứng dụng desktop PyQt6 phục vụ thu nhận ảnh/video từ camera, điều khiển cơ cấu chấp hành qua cổng serial, quản lý dữ liệu thí nghiệm theo Project/Item và đo góc tiếp xúc của giọt chất lỏng. Bản 1.1.0 tổ chức theo hướng MVVM: `Presentation` điều phối giao diện, `Models` chứa nghiệp vụ/thuật toán, `Infrastructure` cung cấp lưu trữ và tra cứu tài nguyên, còn `ReSource` chứa QSS và icon.

## Annotated Directory Structure

- `main.py` — tạo `QApplication`, splash screen, `MainView` và bắt đầu Qt event loop.
- `App/` — toàn bộ mã chạy chính theo các lớp Presentation, Models, Infrastructure và tài nguyên giao diện.
- `App/Models/Analysis/` — thuật toán baseline, fit ellipse/circle và tính góc tiếp xúc inside-liquid.
- `App/Models/Vision/` — quét camera, luồng lấy frame, retry và phân phối frame đến editor đang hoạt động.
- `App/Models/MediaUtils/` — chụp PNG và ghi MP4 trên worker thread.
- `App/Infrastructure/` — SQLite repositories và helper tìm tài nguyên khi chạy source/PyInstaller.
- `App/Presentation/` — MainView, ViewModels, dialogs, sidebar và các editor ảnh/video/camera.
- `App/ReSource/` — stylesheet QSS, SVG, ICO và splash image.
- `Document/` — tài liệu tham chiếu, ảnh thiết kế và các project mẫu.
- `Test/` — prototype/lịch sử thử nghiệm; đây không phải test suite tự động của bản production.
- `requirements.txt` — dependency Python đã ghim phiên bản.
- `TNH_Optima.spec` — cấu hình thu thập module/data/native libraries cho PyInstaller.
- `installer.iss` — cấu hình bộ cài TNH Optima 1.1.0.

## Core Algorithms & Implementation

- **Đo baseline:** hai điểm `(x1,y1)`, `(x2,y2)` được đổi thành đường thẳng `a*x + b*y + c = 0` với `a=dy`, `b=-dx`, `c=dx*y1-dy*x1`. Mirror Image Method hiện là placeholder và trả về `None`.
- **Khởi tạo ellipse:** Fitzgibbon Direct Ellipse Fit giải bài toán trị riêng tổng quát của conic `Ax²+Bxy+Cy²+Dx+Ey+F=0`, chỉ giữ nghiệm thỏa `4AC-B²>0`, rồi đổi sang tâm, bán trục và góc quay.
- **Tinh chỉnh ellipse:** SciPy `least_squares` tối ưu residual Sampson-like có robust loss `soft_l1`. Điểm gần baseline được tăng trọng số theo khoảng cách chuẩn hóa để ổn định tiếp tuyến tại đường tiếp xúc.
- **Góc tiếp xúc:** tìm hai giao điểm giữa baseline và ellipse/circle, hướng vector baseline vào footprint ướt, chọn nhánh tiếp tuyến đi vào phần chất lỏng rồi lấy góc trong miền `[0°,180°]`. Nhánh `Young-Laplace Fit` hiện là phép fit đường tròn đơn giản, chưa phải nghiệm số đầy đủ của phương trình Young–Laplace có trọng lực.
- **Tự phát hiện biên:** grayscale → Gaussian blur → Otsu inverse threshold → morphology close → contour ngoài lớn nhất → bỏ vùng đáy 10% → lấy mẫu đều → đổi pixel sang miền vật lý 5 mm × 3 mm.
- **Camera:** `HardwareCameraScan` tìm thiết bị bằng DirectShow/pygrabber hoặc probe OpenCV; `CameraThread` đọc frame ngoài UI thread; `CameraManager` định tuyến preview/live frame và retry tối đa năm lần.
- **Ghi media:** ảnh được lưu PNG lossless; video dùng hàng đợi `deque(maxlen=5)`, bỏ frame cũ khi nghẽn và ghi MP4V ở worker thread.
- **Điều khiển motor:** input được chuẩn hóa rồi đóng gói serial dưới dạng `#{direction},{distance},{speed},{stop_step}!`; `CCW` đi lên, `CW` đi xuống, `stop_step=-1` là dừng.
- **Project/session:** project hợp lệ có `config.json`; mỗi Item có `Image/` và `Video/`. Trạng thái project/editor/sidebar được JSON-encode vào SQLite.

## Data Flow

1. `main.py` khởi tạo Qt → `MainView` tạo `MainViewModel` → nạp cấu hình camera/hardware và khôi phục session từ SQLite.
2. Thao tác menu/sidebar → signal của View → handler trong ViewModel → manager/repository → cập nhật filesystem/SQLite → signal phản hồi để đồng bộ cây và tab.
3. Camera → OpenCV `VideoCapture` trong `CameraThread` → `QImage` → `CameraManager` → `CameraFrameDispatcher` → `FileEditorViewModel` → preview, chụp ảnh hoặc hàng đợi ghi video.
4. Ảnh → `DropletAnalysisViewModel` chuyển sang grayscale NumPy → người dùng/auto-detect cung cấp baseline và profile points → `AnalysisManager` fit hình học → trả hai góc/tiếp điểm/tiếp tuyến → Matplotlib vẽ và lưu kết quả vào `Item/Image`.
5. Lệnh motor → editor/dialog → `ControlPanelManager` → `HardwareManager` → singleton `HardwareConnector` → cổng serial.
6. Khi đóng ứng dụng → đóng editor/worker/camera → lưu project đang mở, tab và trạng thái expanded vào `SessionData.db`.
