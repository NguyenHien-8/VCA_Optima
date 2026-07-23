# App / Models / Controllers

## Project Overview

Adapter giao tiếp cổng serial và lớp quản lý trạng thái kết nối phần cứng.

## Annotated Directory Structure

- `HardwareConnector.py` — singleton bọc pyserial, quét port, connect/retry/write/disconnect.
- `HardwareManager.py` — QObject facade, giữ config và phát `connection_status_changed`.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Connector chuẩn hóa port/baud, đóng kết nối cũ, thử mở tối đa ba lần và chờ thêm khi Windows báo Access Denied.
- Timeout đọc/ghi 0.1 giây giúp tránh khóa UI; lỗi write làm connector tự disconnect.
- Manager cô lập signal Qt khỏi implementation pyserial.

## Data Flow

1. Dialog cấu hình → `HardwareManager.connect_hardware()`.
2. Manager → singleton `HardwareConnector` → `serial.Serial`.
3. Kết quả kết nối phát signal về status bar; command motor được encode UTF-8 và ghi ra port.

