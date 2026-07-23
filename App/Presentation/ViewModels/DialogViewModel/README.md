# App / Presentation / ViewModels / DialogViewModel

## Project Overview

ViewModels nhỏ cho camera, hardware, motor và quyết định Save/Delete, giữ dialogs không phụ thuộc trực tiếp vào implementation nghiệp vụ.

## Annotated Directory Structure

- `ConfigCameraViewModel.py` — scan/select/preview/apply/revert camera.
- `ConfigHardwareViewModel.py` — scan port, đọc config, apply connection.
- `MotorControlViewModel.py` — chuyển thao tác up/down/stop và phát state.
- `DeleteResourcesViewModel.py` — dữ liệu dialog và cờ delete-on-disk.
- `SaveResourcesViewModel.py` — state `SAVE`, `DONT_SAVE`, `CANCEL`.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Camera dialog áp dụng thay đổi transaction-like: giữ original ID, preview lựa chọn, apply để persist hoặc revert khi cancel.
- Motor ViewModel phát trạng thái trước/sau lệnh đồng bộ.
- Save/Delete ViewModels chỉ giữ state quyết định, không tự sửa filesystem.

## Data Flow

1. Dialog cập nhật ViewModel.
2. ViewModel gọi backend/manager hoặc lưu lựa chọn.
3. Dialog accept/reject; MainView mới thực thi hành động phá hủy/lưu tương ứng.

