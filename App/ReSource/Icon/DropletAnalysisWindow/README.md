# App / ReSource / Icon / DropletAnalysisWindow Icons

## Project Overview

Bộ SVG cho các công cụ trong cửa sổ đo góc tiếp xúc.

## Annotated Directory Structure

- `actualsize.svg` — reset zoom.
- `baseline.svg` — chọn baseline.
- `autodetectedge.svg` — tự phát hiện biên.
- `point.svg` — thêm/xử lý điểm đo.

## Core Algorithms & Implementation

- SVG là dữ liệu vector tĩnh; Qt chịu trách nhiệm rasterize theo DPI/kích thước.
- Asset được tra cứu bằng feature-relative path và có fallback khi thiếu.

## Data Flow

1. Toolbar tạo QIcon từ SVG.
2. User click action → DropletAnalysisWindow cập nhật interaction state.
3. Kết quả được vẽ bằng Matplotlib, không sửa asset.

