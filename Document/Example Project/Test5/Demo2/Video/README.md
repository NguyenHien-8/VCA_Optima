# Document / Example Project / Test5 / Demo2 / Video

## Project Overview

Kho video của Item mẫu `Demo2`. Dữ liệu phục vụ kiểm thử playback/capture; thư mục có thể trống.

## Annotated Directory Structure

- Thư mục dữ liệu hiện đang trống; README này mô tả contract của vị trí.

## Core Algorithms & Implementation

- Không có code tại đây; production ghi MP4V bằng VideoRecorderThread và phát lại qua `QMediaPlayer`.
- Sidebar Release 1.1.0 chỉ liệt kê `.mp4` trong node Video.
- VideoEditor có thể lấy frame hiện tại, đóng dấu thời gian phát và lưu PNG sang sibling `Image/`.

## Data Flow

1. Camera live → queue ghi video → file MP4 trong Video.
2. Sidebar watcher phát hiện file → user mở bằng VideoEditor.
3. Capture frame → PNG được ghi sang `../Image` và xuất hiện trong sidebar.

