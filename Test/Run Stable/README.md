# Test / Run Stable

## Project Overview

Snapshot ứng dụng camera tối giản từng được dùng để kiểm chứng quét thiết bị, đổi camera và hiển thị frame trước khi tích hợp vào kiến trúc hiện tại.

## Annotated Directory Structure

- `main.py` — entry point prototype.
- `MainWindow.py` — UI camera selector/preview.
- `MenuBar.py` — menu thử nghiệm.
- `CameraManager.py` — quản lý scan/change/retry.
- `CameraThread.py` — đọc OpenCV frame.
- `HardwareCameraScan.py` — probe camera.

## Core Algorithms & Implementation

- Scanner chạy QThread, CameraThread đổi BGR→RGB QImage và manager retry khi mất tín hiệu.
- Implementation production trong `App/Models/Vision` bổ sung friendly names, resolution guards, preview routing, cleanup và reference count.

## Data Flow

1. Prototype main → MainWindow.
2. MainWindow → CameraManager scan/select.
3. CameraThread → QImage → preview label; file không tham gia runtime Release 1.1.0.

