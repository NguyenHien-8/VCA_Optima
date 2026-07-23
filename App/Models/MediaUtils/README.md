# App / Models / MediaUtils

## Project Overview

Dịch vụ thu media theo Item: chụp frame camera thành PNG và ghi stream thành MP4 mà không khóa giao diện.

## Annotated Directory Structure

- `MediaManager.py` — facade image/video.
- `ImageCaptureManager.py` — tạo `Image/`, đặt tên timestamp và lưu `QImage` PNG.
- `VideoRecorderManager.py` — state machine và worker thread ghi `Video/video_*.mp4`.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Video state machine có `IDLE`, `RECORDING`, `PAUSED`.
- `VideoRecorderThread` dùng `deque(maxlen=5)` có mutex/condition; khi backlog, chỉ giữ frame mới nhất.
- Frame `QImage` được copy, đổi RGB→BGR và khởi tạo `cv2.VideoWriter` theo kích thước frame đầu.
- Tên file dùng timestamp giây; ảnh PNG lossless, video codec MP4V.

## Data Flow

1. `FileEditorViewModel` nhận frame từ dispatcher.
2. Capture gọi `QImage.save()` vào `Item/Image`.
3. Record đẩy frame vào queue → worker đổi định dạng/ghi `Item/Video` → sidebar watcher tự refresh.

