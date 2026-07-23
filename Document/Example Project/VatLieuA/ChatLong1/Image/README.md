# Document / Example Project / VatLieuA / ChatLong1 / Image

## Project Overview

Kho ảnh của Item mẫu `ChatLong1`. Đây là dữ liệu đầu vào/đầu ra để kiểm thử ImageEditor và Droplet Analysis, không phải source code.

## Annotated Directory Structure

- File hiện có (12): `Image1.png`, `Image2.png`, `Image3.png`, `Image4.png`, `Image5.png`, `Test1.png`, `Test2.png`, `Test3.png`, `Test3_20260422_184225.png`, `Test4.png`, `Test4_20260422_184008.png`, `Test5.png`.

## Core Algorithms & Implementation

- Thư mục không thực thi thuật toán; ảnh được production đọc thành `QPixmap`, chuyển grayscale NumPy khi phân tích và có thể nhận ảnh capture/overlay PNG mới.
- Sidebar chỉ nhận `.jpg`, `.jpeg`, `.png`; file khác không được hiện như image node.
- Tên dạng `TNH_YYYYMMDD_HHMMSS.png`, `capture_*` hoặc `*_timestamp.png` phản ánh các luồng camera, video capture và analysis export.

## Data Flow

1. Project/Item được mở → sidebar quét thư mục Image.
2. Double click ảnh → ImageEditor; calibration chuyển pixmap sang DropletAnalysisWindow.
3. Camera capture, video frame capture hoặc analysis save có thể ghi PNG mới → QFileSystemWatcher refresh sidebar.

