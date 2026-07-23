# App / Models / MediaUtils

## Project Overview

Dịch vụ media theo Item: lưu frame camera thành PNG và ghi stream thành MP4 mà không khóa UI.

## Annotated Directory Structure

- `MediaManager.py` — facade thống nhất image/video.
- `ImageCaptureManager.py` — tạo `Image/` và lưu `QImage` lossless.
- `VideoRecorderManager.py` — state machine và recorder thread cho `Video/`.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- File dùng timestamp đến microsecond để tránh ghi đè khi capture liên tiếp.
- Video state machine gồm `IDLE`, `RECORDING`, `PAUSED`.
- `VideoRecorderThread` dùng `deque(maxlen=5)`, mutex và wait condition; frame cũ bị bỏ khi encoder chậm.
- OpenCV/NumPy được import trong recorder thread; `VideoWriter` luôn release trong `finally`.
- Đóng editor chỉ request stop recorder; wrapper thread được giữ sống đến `finished`.

## Data Flow

1. Camera dispatcher gửi `QImage` đến `FileEditorViewModel`.
2. Capture chạy `QImage.save()` trong worker → trả filename → phát `media_created(Image)`.
3. Record copy frame vào queue → recorder ghi MP4 → Stop chạy trong worker và release writer.
4. Stop thành công trả filename → phát `media_created(Video)` → SideBar hiển thị file ngay.
