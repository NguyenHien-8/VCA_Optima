# App / Presentation / Views

## Project Overview

Cửa sổ chính và các thành phần UI cấp cao, chịu trách nhiệm lắp ráp ViewModel, Sidebar, menus, dialogs và editor.

## Annotated Directory Structure

- `MainView.py` — application shell, signal wiring, restore và coordinated shutdown.
- `MenuBar.py` — lắp ráp menu cấp cao.
- `Dialog/` — cấu hình camera/hardware và dialog xác nhận.
- `Widgets/` — Sidebar, workspace, editors, status và analysis window.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- `camera_dispatcher` được khởi tạo trước mọi deferred callback và chỉ nhận target có `receive_frame`.
- Editor ảnh/video được lazy import theo extension.
- Text lớn được đưa vào editor theo chunk bằng `QTimer`.
- SideBar khởi tạo branch indicator từ kết quả scan nền, không yêu cầu người dùng click trước để phát hiện media.
- MainView hoãn đóng nếu editor hoặc worker chưa an toàn, sau đó tự tiếp tục qua tín hiệu.
- File Editor và Droplet Analysis dùng MainView làm explicit owner; helper đồng bộ transient parent và taskbar thumbnail policy trước lần show đầu và mỗi lần native handle được hiển thị lại.

## Data Flow

1. `MainViewModel` phát project/item/file/session signals.
2. MainView kết nối signals đến Sidebar và EditorWorkspace.
3. FileEditor/VideoEditor phát `media_created`; MainView nối trực tiếp tín hiệu này tới Sidebar.
4. Sidebar selection thay đổi storage target của FileEditor.
5. Mở secondary window → MainView owner + shared AppUserModelID/taskbar style → grouped preview và coordinated minimize/restore.
6. Close event thu editor/expanded paths rồi cleanup và lưu session.
