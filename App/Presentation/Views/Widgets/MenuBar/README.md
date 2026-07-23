# App / Presentation / Views / Widgets / MenuBar

## Project Overview

Các menu/action của cửa sổ chính, gồm shortcut, icon và lời gọi API công khai của MainView.

## Annotated Directory Structure

- `MenuFile.py` — Project/Item lifecycle, restart và exit.
- `MenuSetup.py` — camera/hardware configuration.
- `MenuControl.py` — motor dialog và FileEditor control.
- `KeyboardShortcut.py` — shortcut constants.
- `ToggleSideBar.py` — sidebar action/icon.
- `MenuCalibration.py`, `MenuTool.py`, `MenuWindow.py`, `MenuHelp.py` — các menu mở rộng.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Action helper chuẩn hóa `QAction`, icon và `QKeySequence`.
- Config/Motor/FileEditor modules nặng được import trong action handler, không nằm trên startup path.
- Menu chỉ gọi MainView hoặc mở dialog; nghiệp vụ và I/O vẫn đi qua ViewModel/worker.
- Restart dùng Qt process API sau khi yêu cầu application quit.

## Data Flow

1. User chọn menu hoặc shortcut.
2. Action gọi method của MainView.
3. MainView lazy-load dialog/feature nếu cần.
4. Dialog/ViewModel thực hiện nghiệp vụ và trả kết quả bằng signal.
