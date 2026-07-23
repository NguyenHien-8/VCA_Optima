# App / Presentation / Views / Widgets / MenuBar

## Project Overview

Các menu/action của cửa sổ chính, gồm shortcut, icon resource và lời gọi tới API công khai của MainView.

## Annotated Directory Structure

- `MenuFile.py` — New/Open/Save As/Delete/Restart/Exit/Rename.
- `MenuSetup.py` — camera và hardware configuration.
- `MenuControl.py` — motor dialog và standalone control panel.
- `KeyboardShortcut.py` — hằng shortcut.
- `ToggleSideBar.py` — QAction và icon vẽ bằng QPainter.
- `MenuCalibration.py`, `MenuTool.py`, `MenuWindow.py`, `MenuHelp.py` — menu placeholder hiện chưa gắn vào menu bar.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Action helper tạo `QAction`, icon và `QKeySequence` nhất quán.
- Restart gọi `QApplication.quit()` rồi `QProcess.startDetached(sys.executable, sys.argv)`.
- Rename là hidden action gắn `Ctrl+R` trực tiếp vào MainView.

## Data Flow

1. User chọn menu/shortcut.
2. Action gọi method của MainView hoặc mở dialog.
3. MainView chuyển yêu cầu vào ViewModel/manager.

