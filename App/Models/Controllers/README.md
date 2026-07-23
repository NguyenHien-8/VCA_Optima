# App / Models / Controllers

## Project Overview

Tầng controller sở hữu kết nối serial duy nhất và cung cấp API phần cứng thread-safe cho phần còn lại của ứng dụng.

## Annotated Directory Structure

- `HardwareConnector.py` — singleton serial, scan port, connect/disconnect và write.
- `HardwareManager.py` — facade QObject, cấu hình hiện tại và signal trạng thái.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Singleton được bảo vệ bằng lock; serial handle được thay thế/đóng theo ownership rõ ràng.
- Mỗi yêu cầu connect có generation token: disconnect hoặc connect mới sẽ hủy kết quả connect cũ.
- Retry chỉ áp dụng cho lỗi truy cập port và chạy trong worker, không giữ lock trong lúc sleep/open port.
- Read/write timeout hữu hạn; port, baud và payload được kiểm tra chủ động.

## Data Flow

1. Dialog/MainViewModel gửi connect hoặc scan vào `FunctionWorker`.
2. `HardwareManager` gọi `HardwareConnector`.
3. Connector trả `(success, message)` và Manager phát `connection_status_changed`.
4. Motor command đi từ ViewModel → `ControlPanelManager` → `HardwareManager` → serial.
