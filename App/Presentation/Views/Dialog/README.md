# App / Presentation / Views / Dialog

## Project Overview

Các QDialog cấu hình camera/hardware, điều khiển motor và xác nhận save/delete.

## Annotated Directory Structure

- `ConfigCameraDialog.py` — camera list, preview và apply/revert.
- `ConfigHardwareDialog.py` — port scan, baud/query period và connect.
- `MotorControlDialog.py` — up/down/stop command queue.
- `DeleteResourcesDialog.py` — lựa chọn remove workspace hoặc delete disk.
- `SaveResourcesDialog.py` — Save/Don't Save/Cancel.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Hardware port scan và connect chạy trong `FunctionWorker`; nút được khóa trong lúc thao tác.
- Motor commands chạy tuần tự trong worker; Stop được đưa lên đầu queue.
- Dialog từ chối đóng khi worker liên quan chưa hoàn tất để tránh QThread bị hủy sớm.
- Camera preview dùng lifecycle bất đồng bộ của `CameraManager`.
- Dialog xác nhận chỉ trả decision, không tự thực hiện thao tác phá hủy.

## Data Flow

1. Menu/MainView lazy-import và mở dialog với manager phù hợp.
2. Dialog validate input rồi giao tác vụ blocking cho worker.
3. Worker result cập nhật UI trên main thread.
4. Accept/reject trả quyền điều phối về MainView/ViewModel.
