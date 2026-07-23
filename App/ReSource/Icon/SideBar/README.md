# App / ReSource / Icon / SideBar Icons

## Project Overview

SVG cho node media và mũi tên mở/đóng trong project tree.

## Annotated Directory Structure

- `image_file.svg`, `video_file.svg`, `file_tnh.svg` — loại node.
- `arrow_down.svg`, `arrow_next.svg` — trạng thái expanded/collapsed.

## Core Algorithms & Implementation

- SVG là dữ liệu vector tĩnh; Qt chịu trách nhiệm rasterize theo DPI/kích thước.
- Asset được tra cứu bằng feature-relative path và có fallback khi thiếu.

## Data Flow

1. Sidebar nạp icon lúc khởi tạo.
2. Filesystem data tạo node đúng icon.
3. Tree paint disclosure arrow theo expanded state.

