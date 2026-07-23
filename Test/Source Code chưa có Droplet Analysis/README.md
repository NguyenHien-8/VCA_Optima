# Test / Source Code chưa có Droplet Analysis

## Project Overview

Snapshot ImageEditor trước khi tính năng Droplet Analysis được thêm vào, dùng làm mốc so sánh UI và hành vi load/save/zoom.

## Annotated Directory Structure

- `ImageEditor.py` — editor ảnh cơ bản.
- `ImageEditorViewModel.py` — load/save pixmap và state đơn giản.

## Core Algorithms & Implementation

- Chức năng tập trung vào hiển thị, zoom/pan và lưu ảnh; không có baseline, edge fitting hoặc contact-angle calculation.
- Diff ý tưởng với production thể hiện phần phân tích được bổ sung qua `DropletAnalysisViewModel` và `DropletAnalysisWindow` thay vì nhồi vào editor gốc.

## Data Flow

1. File dialog → ImageEditorViewModel load QPixmap.
2. Signal image_loaded → editor render.
3. Bản production có thể mở cửa sổ phân tích từ pixmap này.

