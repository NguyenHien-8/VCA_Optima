# Document / Example Project / Test4 / Demo1 / Image

## Project Overview

Kho ảnh của Item mẫu `Demo1`. Đây là dữ liệu đầu vào/đầu ra để kiểm thử ImageEditor và Droplet Analysis, không phải source code.

## Annotated Directory Structure

- File hiện có (5): `Image1.png`, `Image2.png`, `Image3.png`, `Image4.png`, `Image5.png`.

## Core Algorithms & Implementation

- Thư mục không thực thi thuật toán; ảnh được production đọc thành `QPixmap`, chuyển grayscale NumPy khi phân tích và có thể nhận ảnh capture/overlay PNG mới.
- Sidebar chỉ nhận `.jpg`, `.jpeg`, `.png`; file khác không được hiện như image node.
- Tên dạng `TNH_YYYYMMDD_HHMMSS.png`, `capture_*` hoặc `*_timestamp.png` phản ánh các luồng camera, video capture và analysis export.

## Data Flow

1. Project/Item được mở → sidebar quét thư mục Image.
2. Double click ảnh → ImageEditor; calibration chuyển pixmap sang DropletAnalysisWindow.
3. Camera capture, video frame capture hoặc analysis save có thể ghi PNG mới → QFileSystemWatcher refresh sidebar.

