# App / Presentation

## Project Overview

Tầng trình bày PyQt6 tổ chức theo MVVM, chịu trách nhiệm widget, signal/slot, worker orchestration và lifecycle UI.

## Annotated Directory Structure

- `ViewModels/` — state, validation, worker và adapter tới Models.
- `Views/` — MainView, dialogs, workspace, sidebar và feature widgets.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- View không thực hiện filesystem, serial hoặc phân tích nặng trực tiếp.
- Kết quả worker quay lại UI qua Qt queued signal.
- Editor nặng được import tại điểm sử dụng để giảm startup cost.
- Close event có thể bị hoãn khi worker đang chạy; `close_ready` tiếp tục thao tác sau khi tài nguyên an toàn.

## Data Flow

1. User event bắt đầu tại View.
2. ViewModel validate và gọi Model/worker.
3. Signal kết quả cập nhật widget trên UI thread.
4. Capture/record phát sự kiện media cụ thể thay vì chỉ phụ thuộc filesystem watcher.
5. Shutdown thu session state, dừng worker/device và giải phóng widget theo thứ tự.
