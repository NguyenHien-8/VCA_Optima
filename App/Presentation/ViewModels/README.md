# App / Presentation / ViewModels

## Project Overview

Các ViewModel kết nối giao diện với nghiệp vụ, đồng thời quản lý worker và trạng thái phiên ở cấp ứng dụng.

## Annotated Directory Structure

- `MainViewModel.py` — composition root, CRUD project/item/file, clipboard, restore/save session, camera/hardware.
- `Workers.py` — QThread copy/move folder, copy/move media, load text và placeholder vision worker.
- `DialogViewModel/` — adapter state cho dialogs.
- `FeatureViewModel/` — state/logic cho image, file-camera và droplet editors.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Copy/cut folder/file chạy nền và trả signal có đủ context đích để UI cập nhật đúng node.
- Text loader giới hạn 20 MB và từ chối binary/non-UTF-8; MainView hỏi xác nhận từ 5 MB.
- Trước rename/delete, ViewModel yêu cầu View đóng editor và watcher để giải phóng file handle.
- Camera `acquire/release` gắn với lifecycle editor; session lưu project, editors, expanded paths và opened items.

## Data Flow

1. View event → handler `handle_*`.
2. Handler → manager hoặc worker.
3. Worker/model result → ViewModel signal → MainView/sidebar/editor.
4. Shutdown → stop workers/camera → serialize session.

