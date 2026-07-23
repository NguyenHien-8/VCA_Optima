# App / Presentation

## Project Overview

Lớp trình bày PyQt6 tổ chức theo MVVM, chịu trách nhiệm UI, signal/slot, tab editor và dialogs.

## Annotated Directory Structure

- `ViewModels/` — điều phối Models và state dành cho View.
- `Views/` — cửa sổ, dialog và widget.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Qt signal/slot tách UI events khỏi nghiệp vụ và cho phép worker threads trả kết quả an toàn.
- `MainViewModel` là composition root của managers/repositories; `MainView` lắp ráp widget và kết nối signals.
- View chỉ giữ state hiển thị/ngắn hạn; project, device và persistence đi qua Models.

## Data Flow

1. User event phát từ View.
2. ViewModel gọi Model/worker và phát status/result signals.
3. View cập nhật widget; khi đóng, ViewModel lưu session và cleanup worker/device.

