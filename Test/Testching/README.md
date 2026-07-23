# Test / Testching

## Project Overview

Tập hợp thử nghiệm thủ công không đồng nhất cho camera, sidebar, menu, file editor và analyzer; tên thư mục được giữ theo lịch sử repository.

## Annotated Directory Structure

- `main.py`, `MainWindow.py` — shell thử nghiệm.
- `CameraThread.py`, `CameraScanThread.py`, `HardwareCameraScan.py`, `CameraManager.py` — camera variants.
- `SideBar_Old.py`, `MenuFile.py`, `FileEditor.py` — UI prototypes.
- `ImageEditor.py`, `ImageEditorViewModel.py`, `DropletAnalyzer.py` — image/droplet prototype.
- `Hien.py` — file rỗng placeholder.

## Core Algorithms & Implementation

- Camera variants kiểm thử QThread, scan indices, pause/change và retry.
- Sidebar prototype xây cây Project/Item/media, drag/drop và QFileSystemWatcher; phần ổn định được chuyển vào production SideBar.
- Droplet prototype dùng contour/circle geometry đời đầu.
- Không có assertion hay automated coverage; các import `Src.*` có thể không còn hợp lệ.

## Data Flow

1. Mỗi file/prototype được chạy độc lập.
2. Developer quan sát UI/device behavior.
3. Ý tưởng phù hợp được chuyển sang `App`; các file còn lại chỉ là tham chiếu lịch sử.

