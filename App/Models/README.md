# App / Models

## Project Overview

Lớp nghiệp vụ trung tâm: quản lý cây project, session, camera, media, phần cứng và phân tích góc tiếp xúc.

## Annotated Directory Structure

- `Analysis/` — baseline, ellipse/circle fit và contact-angle geometry.
- `Controllers/` — serial connector/manager.
- `MediaUtils/` — chụp ảnh và ghi video.
- `Vision/` — camera scanning, capture thread và frame routing.
- `ProjectManager.py` — lifecycle Project/Item/media file.
- `SessionManager.py` — state cache và persistence orchestration.
- `CamHardwareManager.py` — backend cấu hình camera/hardware.
- `ControlPanelManager.py` — chuẩn hóa lệnh motor.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Project có marker `config.json`; Item hợp lệ phải có cả `Image/` và `Video/`.
- Camera và serial được bọc sau manager để ViewModel không thao tác API thiết bị trực tiếp.
- Các thuật toán số trả dictionary/tuple thuần để dễ hiển thị và kiểm thử.

## Data Flow

1. ViewModel nhận yêu cầu từ UI.
2. Model kiểm tra trạng thái và thực hiện filesystem/thiết bị/phân tích.
3. Kết quả trả trực tiếp hoặc phát signal về ViewModel/View.

