# App / Presentation / Views

## Project Overview

Cửa sổ chính và các thành phần giao diện cấp cao của ứng dụng.

## Annotated Directory Structure

- `MainView.py` — lắp ráp sidebar, menu, status, tab/workspace, restore và shutdown.
- `MenuBar.py` — tạo File/Setup/Control menus và toggle sidebar.
- `Dialog/` — các dialog cấu hình/xác nhận.
- `Widgets/` — sidebar, editors, analysis window, status và menu widgets.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- `MainView` chọn editor theo extension: image, video hoặc text.
- Tab uniqueness dựa trên normalized full path; rename/delete dừng player/đóng editor trước khi sửa file.
- Khi đóng app, View thu editor list và expanded paths trước, xử lý unsaved text, cleanup rồi lưu session.

## Data Flow

1. ViewModel signals thêm/xóa/đổi tên node trong sidebar.
2. Double click/drag-drop sidebar mở file vào workspace.
3. Tab active quyết định ViewModel nhận camera frame.

