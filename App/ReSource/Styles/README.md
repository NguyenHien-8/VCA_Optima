# App / ReSource / Styles

## Project Overview

Các stylesheet QSS tách presentation styling khỏi logic Python.

## Annotated Directory Structure

- `MainViewStyles.qss`, `MenuBarStyles.qss`, `EditorWorkspaceStyles.qss` — shell chính.
- `FileEditorStyles.qss`, `ImageEditorStyles.qss`, `VideoEditorStyles.qss`, `DropletAnalysisStyles.qss` — editors và cửa sổ phân tích.
- `CameraDialogStyles.qss`, `HardwareDialogStyles.qss`, `MotorControlDialog.qss`, `DelSaveDialogStyles.qss` — dialogs.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Qt selector dựa trên widget class, objectName và dynamic property.
- Mỗi View gọi `apply_stylesheet()` để nạp UTF-8 qua resource path; nếu thiếu chỉ cảnh báo và dùng style mặc định.

## Data Flow

1. Widget khởi tạo → resolve QSS path → đọc chuỗi → `setStyleSheet()`.
2. Dynamic property (ví dụ preview state) được repolish để đổi giao diện.
