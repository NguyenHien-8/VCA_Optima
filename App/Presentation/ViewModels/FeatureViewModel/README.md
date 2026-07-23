# App / Presentation / ViewModels / FeatureViewModel

## Project Overview

State và logic dành cho ba feature editor: ảnh, camera/media và phân tích giọt.

## Annotated Directory Structure

- `ImageEditorViewModel.py` — load/save `QPixmap`.
- `FileEditorViewModel.py` — nhận camera frame, motor command, capture/record và timer.
- `DropletAnalysisViewModel.py` — chuyển pixmap sang grayscale NumPy, statistics và heatmap grid.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Droplet image conversion dùng `QBuffer` PNG + PIL để tránh lỗi truy cập bộ nhớ QImage; chuẩn hóa intensity và tạo mesh 5×3 mm.
- File editor chỉ đổi storage target khi không recording; target mới tạo `MediaManager` mới.
- Recording timer là QTimer 1 giây; FPS ghi lấy từ camera, fallback 30.

## Data Flow

1. View/editor gọi feature ViewModel.
2. ViewModel chuyển đổi dữ liệu hoặc gọi Media/Control managers.
3. Signals frame/state/error/analysis trả lại widget.

