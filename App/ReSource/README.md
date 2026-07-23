# App / ReSource

## Project Overview

Tài nguyên giao diện được đóng gói cùng executable. Tên thư mục giữ nguyên casing hiện tại vì mọi đường dẫn trong mã tham chiếu `App/ReSource`.

## Annotated Directory Structure

- `Styles/` — QSS theo widget/dialog.
- `Icon/` — ICO, PNG và SVG theo feature.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Không có thuật toán nghiệp vụ; QSS áp dụng qua `setStyleSheet`, icon qua `QIcon`.
- `ResourceHelper.resource_path()` làm cho cùng đường dẫn hoạt động ở source và `_MEIPASS`.
- `TNH_Optima.spec` bundle toàn bộ `App` nên tài nguyên có mặt trong bản build.

## Data Flow

1. View yêu cầu resource tương đối.
2. ResourceHelper trả path tuyệt đối.
3. Qt tải style/icon/splash khi tạo widget.

