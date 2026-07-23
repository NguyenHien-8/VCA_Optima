# Document / Example Project / Test2 / dfndnnd / Image

## Project Overview

Kho ảnh của Item mẫu `dfndnnd`. Đây là dữ liệu đầu vào/đầu ra để kiểm thử ImageEditor và Droplet Analysis, không phải source code.

## Annotated Directory Structure

- File hiện có (4): `capture_20260228_150721.png`, `capture_20260228_174425.png`, `capture_20260301_202310.png`, `z7597627211167_963235ef7ffef6746e5e76e701c3b483.jpg`.

## Core Algorithms & Implementation

- Thư mục không thực thi thuật toán; ảnh được production đọc thành `QPixmap`, chuyển grayscale NumPy khi phân tích và có thể nhận ảnh capture/overlay PNG mới.
- Sidebar chỉ nhận `.jpg`, `.jpeg`, `.png`; file khác không được hiện như image node.
- Tên dạng `TNH_YYYYMMDD_HHMMSS.png`, `capture_*` hoặc `*_timestamp.png` phản ánh các luồng camera, video capture và analysis export.

## Data Flow

1. Project/Item được mở → sidebar quét thư mục Image.
2. Double click ảnh → ImageEditor; calibration chuyển pixmap sang DropletAnalysisWindow.
3. Camera capture, video frame capture hoặc analysis save có thể ghi PNG mới → QFileSystemWatcher refresh sidebar.

