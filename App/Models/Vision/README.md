# App / Models / Vision

## Project Overview

Pipeline camera đa luồng: khám phá thiết bị, đọc frame, xử lý mất kết nối và chuyển frame đến đúng editor.

## Annotated Directory Structure

- `HardwareCameraScan.py` — QThread quét camera bằng pygrabber/DirectShow hoặc OpenCV fallback.
- `CameraThread.py` — QThread sở hữu `VideoCapture`, pause/stop bằng mutex và wait condition.
- `CameraManager.py` — lifecycle, resolution guard, retry, preview/live routing và reference count.
- `CameraFrameDispatcher.py` — giữ last frame và forward đến active ViewModel.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Windows ưu tiên friendly names từ pygrabber; fallback probe index 0..4 và xác nhận bằng một frame đọc được.
- Resolution bị giới hạn 480×360 đến 960×576; mặc định 640×480.
- Mất frame phát error; manager thử lại sau 1 giây, tối đa năm lần.
- Reference count chỉ duy trì camera khi có editor sử dụng; dispatcher gửi last frame ngay khi chuyển active editor.

## Data Flow

1. Scanner → danh sách `{index,name}` → dialog/status.
2. `CameraThread` → BGR frame → RGB `QImage.copy()` → `CameraManager`.
3. Manager phát preview hoặc live signal → dispatcher → active `FileEditorViewModel`.

