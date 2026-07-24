# App / Presentation / ViewModels

## Project Overview

ViewModels kết nối Views với Models, quản lý worker và phát các signal có ngữ cảnh đầy đủ cho UI.

## Annotated Directory Structure

- `MainViewModel.py` — composition root, project/file commands, session, camera và hardware.
- `Workers.py` — callable worker, session restore, file loader và media/file operations.
- `FeatureViewModel/` — image, file-camera/media và droplet analysis.
- `DialogViewModel/` — adapter cho dialogs cấu hình/xác nhận.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Session restore, project CRUD, file load/save, serial connect và các tác vụ nặng chạy nền.
- Text save dùng temporary file, flush/fsync và `os.replace`.
- Worker được track, request interruption khi đóng và `deleteLater()` sau `finished`.
- Timer trì hoãn có parent và được hủy trong shutdown.
- File loader giới hạn 20 MB và từ chối binary/non-UTF-8.
- Session restore xếp Project theo normalized path rank và Item theo case-insensitive saved rank; node mới hoặc thiếu metadata được đặt sau theo thứ tự tên ổn định.

## Data Flow

1. View gọi handler hoặc feature method.
2. ViewModel tạo worker và lưu ownership.
3. Result signal gọi callback trên UI thread rồi cập nhật View.
4. `FileEditorViewModel.media_created` mang project, item, media type và full path đến SideBar.
5. Shutdown chỉ hoàn tất khi các worker liên quan đã dừng.
6. MainView snapshot `sidebar_order` → MainViewModel lọc các Project còn tồn tại → SessionManager lưu → SessionRestoreWorker trả Project/Item theo đúng thứ tự.
