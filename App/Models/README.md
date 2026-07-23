# App / Models

## Project Overview

Tầng nghiệp vụ quản lý project/session, camera, phần cứng serial, media và phân tích hình học. Models không thao tác widget trực tiếp.

## Annotated Directory Structure

- `Analysis/` — baseline, contour, circle/ellipse fit và contact-angle geometry.
- `Controllers/` — serial connector và hardware facade.
- `MediaUtils/` — capture PNG và record MP4.
- `Vision/` — scan camera, capture thread, lifecycle và frame dispatcher.
- `ProjectManager.py` — CRUD Project/Item/media với kiểm tra đường dẫn.
- `SessionManager.py` — snapshot và restore trạng thái phiên.
- `CamHardwareManager.py` — backend cấu hình camera/hardware.
- `ControlPanelManager.py` — validate và đóng gói lệnh motor.

## Core Algorithms & Implementation

- Project hợp lệ có marker `config.json`; Item hợp lệ có `Image/` và `Video/`.
- Các thao tác filesystem được serialize bằng khóa model và chạy trong worker.
- Camera/serial/media sử dụng owner duy nhất, timeout hữu hạn và cooperative cancellation.
- Tên/path được chuẩn hóa, kiểm tra containment và chống `..`/ký tự không hợp lệ.

## Data Flow

1. ViewModel gửi yêu cầu đã validate vào Model.
2. Model thao tác filesystem, thiết bị hoặc thuật toán trong worker phù hợp.
3. Kết quả tuple/object thuần được trả về ViewModel.
4. ViewModel phát signal trạng thái, lỗi hoặc thay đổi tài nguyên cho View.
