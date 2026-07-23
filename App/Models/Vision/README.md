# App / Models / Vision

## Project Overview

Quản lý camera vật lý, scan thiết bị và định tuyến frame đến feature đang hoạt động.

## Annotated Directory Structure

- `CameraManager.py` — state machine camera, reference count, retry timer và lifecycle.
- `CameraThread.py` — mở/capture/release OpenCV camera ngoài UI thread.
- `HardwareCameraScan.py` — scan tên/index camera trong worker.
- `CameraFrameDispatcher.py` — chuyển frame đến ViewModel hợp lệ.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Camera không scan hoặc kết nối trong constructor; I/O chỉ bắt đầu sau first paint hoặc khi feature acquire.
- Chuyển camera dùng pending target và tín hiệu `finished`, không gọi wait trên luồng UI.
- Retry dùng single-shot `QTimer` có thể hủy.
- Thread kiểm tra interruption, giải phóng `VideoCapture` trong `finally` và chỉ import OpenCV trong `run()`.
- Dispatcher kiểm tra callable `receive_frame`; target lỗi sẽ bị vô hiệu hóa an toàn.

## Data Flow

1. Config/feature yêu cầu scan, preview hoặc acquire camera.
2. `CameraManager` tạo worker và nhận `QImage` qua queued signal.
3. `CameraFrameDispatcher` chuyển frame đến `FileEditorViewModel`.
4. ViewModel phát preview, capture frame hoặc đưa frame vào video recorder.
