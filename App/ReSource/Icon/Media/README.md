# App / ReSource / Icon / Media Icons

## Project Overview

Bộ SVG dùng trong image/video/camera editors.

## Annotated Directory Structure

- Open/capture/analysis icons cho ảnh.
- Play/pause/stop/skip icons cho video.
- Photo/video camera icons cho live capture và recording.

## Core Algorithms & Implementation

- SVG là dữ liệu vector tĩnh; Qt chịu trách nhiệm rasterize theo DPI/kích thước.
- Asset được tra cứu bằng feature-relative path và có fallback khi thiếu.

## Data Flow

1. Editor khởi tạo icon paths.
2. QPushButton nhận QIcon.
3. Signal click đi vào ViewModel/media pipeline.

