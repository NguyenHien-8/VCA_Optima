# App / Presentation / Views / Widgets

## Project Overview

Tập hợp widget dùng lại cho navigation, editor workspace, trạng thái và cửa sổ phân tích.

## Annotated Directory Structure

- `SideBar.py` — cây Project/Item/Image/Video và filesystem watcher.
- `EditorWorkspace.py` — tab container, drag/drop và path deduplication.
- `DropletAnalysisWindow.py` — UI tương tác và overlay contact angle.
- `StatusBar.py` — trạng thái camera/serial.
- `FileEditorWorkspace/` — camera, image, video, motor/media controls.
- `MenuBar/` — menu actions và shortcuts.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Sidebar watcher đồng bộ file media mới vào cây mà không cần restart.
- Editor tab bar tự reorder theo drag threshold và giữ metadata bằng Qt properties.
- Droplet window quản lý point placement/drag/delete, zoom/pan, fit và export Matplotlib.

## Data Flow

1. ProjectModel signals → sidebar tree.
2. Sidebar selection/drag/drop → editor workspace.
3. Editor/analysis signals → ViewModel → Models và quay lại widget.

