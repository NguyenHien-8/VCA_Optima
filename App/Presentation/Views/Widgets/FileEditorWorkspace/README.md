# App / Presentation / Views / Widgets / FileEditorWorkspace

## Project Overview

Các editor và control widget cho camera live, ảnh tĩnh và video đã lưu.

## Annotated Directory Structure

- `FileEditor.py` — ghép camera preview với motor/media controls.
- `MotorControlEditor.py` — nhập height/speed và phát lệnh.
- `MediaControlEditor.py` — capture/record/pause/resume/stop UI state.
- `ImageEditor.py` — hiển thị Matplotlib, zoom/pan, save và mở droplet analysis.
- `VideoEditor.py` — QMediaPlayer, timeline, tốc độ, skip và capture frame.

## Core Algorithms & Implementation

- Image editor ánh xạ mọi ảnh vào extent vật lý 5×3 mm và clamp zoom trong miền đó.
- Video editor dùng `QVideoSink` lấy frame hiện tại; capture ghi PNG vào sibling `Image/` và đóng dấu thời gian phát.
- File editor truyền signal control cho ViewModel; không tự ghi serial/media.
- Đóng image editor sẽ đóng các cửa sổ phân tích con; đóng video giải phóng media source.

## Data Flow

1. Camera dispatcher → `FileEditorViewModel` → `FileEditor` preview/control.
2. Image/Video file từ sidebar → editor tương ứng.
3. Image editor → `DropletAnalysisWindow`; video capture → `Item/Image` → sidebar watcher.

