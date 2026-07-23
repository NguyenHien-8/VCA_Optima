# App / Presentation / Views / Widgets

## Project Overview

Các widget tái sử dụng cho cây project, tab editor, trạng thái và phân tích giọt.

## Annotated Directory Structure

- `SideBar.py` — cây Project/Item/Image/Video, explicit media update và filesystem watcher.
- `EditorWorkspace.py` — tab container, drag/drop và close contract.
- `DropletAnalysisWindow.py` — tương tác điểm, fit, overlay và export.
- `StatusBar.py` — trạng thái camera/serial.
- `FileEditorWorkspace/` — camera, image/video editor và control widgets.
- `MenuBar/` — menu actions, shortcuts và sidebar toggle.

## Core Algorithms & Implementation

- SideBar lazy-scan media bằng worker và chèn kết quả theo batch 200 item.
- `notify_media_created` validate full path, chống duplicate, chèn theo thứ tự và tự mở đúng Project/Item/Image|Video node.
- Nếu watcher phát thay đổi khi scanner đang chạy, refresh được đưa vào pending set và chạy lại sau `finished`.
- Watcher vẫn xử lý file tạo/xóa từ ứng dụng ngoài.
- Widget có worker phát `close_ready` để tránh xóa QThread còn chạy.

## Data Flow

1. Project signals tạo hoặc sửa node cấu trúc.
2. Capture/record thành công → explicit `media_created` → cập nhật SideBar ngay.
3. Filesystem change bên ngoài → watcher → background scan → batched tree update.
4. Double click/drag-drop file → MainView mở editor tương ứng.
