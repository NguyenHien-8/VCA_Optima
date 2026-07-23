# App / ReSource / Icon

## Project Overview

Icon production được nhóm theo feature để menu/widget tải đúng asset.

## Annotated Directory Structure

- `app_icon.ico` — icon executable/window.
- `splash_screen.png` — splash startup.
- `Media/` — ảnh/video/camera actions.
- `MenuFile/`, `MenuControl/` — menu actions.
- `DropletAnalysisWindow/` — measurement tools.
- `SideBar/` — file types và disclosure arrows.

## Core Algorithms & Implementation

- Không có xử lý ảnh runtime ngoài scaling/vẽ bởi Qt.
- Mã luôn kiểm tra `os.path.exists`; khi thiếu icon, một số widget dùng standard icon hoặc text fallback.

## Data Flow

1. View resolve feature icon directory.
2. `QIcon`/`QPixmap` nạp SVG/PNG/ICO.
3. Qt render theo kích thước nút, splash hoặc cây.

