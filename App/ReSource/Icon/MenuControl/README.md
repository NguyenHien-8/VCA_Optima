# App / ReSource / Icon / MenuControl Icons

## Project Overview

SVG cho các action Control.

## Annotated Directory Structure

- `control_panel.svg` — mở standalone FileEditor.
- `filter.svg` — mở Motor Control dialog.

## Core Algorithms & Implementation

- SVG là dữ liệu vector tĩnh; Qt chịu trách nhiệm rasterize theo DPI/kích thước.
- Asset được tra cứu bằng feature-relative path và có fallback khi thiếu.

## Data Flow

1. MenuControl resolve path.
2. Tạo QAction với icon.
3. Action gọi MainView/dialog.

