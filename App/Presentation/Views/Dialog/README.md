# App / Presentation / Views / Dialog

## Project Overview

Các QDialog cấu hình camera/hardware, điều khiển motor và xác nhận lưu/xóa tài nguyên.

## Annotated Directory Structure

- `ConfigCameraDialog.py` — danh sách camera, preview bo góc, apply/cancel.
- `ConfigHardwareDialog.py` — port, baud, query period và kết nối.
- `MotorControlDialog.py` — nhập height/speed, up/down/stop.
- `DeleteResourcesDialog.py` — tùy chọn chỉ bỏ workspace hoặc xóa đĩa.
- `SaveResourcesDialog.py` — Save/Don't Save/Cancel.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Camera preview chuyển `QImage` thành scaled `QPixmap`; Apply kết nối khi editor đang mở, Cancel khôi phục camera ban đầu.
- Hardware dialog validate baud/port trước khi gọi backend.
- Dialogs xác nhận không trực tiếp xóa file; chúng trả decision cho MainView.

## Data Flow

1. Menu/MainView mở dialog với manager/context.
2. Dialog trao đổi với DialogViewModel.
3. Kết quả accept/reject quay về MainView để commit hoặc hủy hành động.

