# App / ReSource / Icon / MenuFile Icons

## Project Overview

SVG cho các thao tác lifecycle Project/Item và ứng dụng.

## Annotated Directory Structure

- New/open/save/delete/rename-related assets.
- `restart.svg` và `exit.svg` cho lifecycle process.

## Core Algorithms & Implementation

- SVG là dữ liệu vector tĩnh; Qt chịu trách nhiệm rasterize theo DPI/kích thước.
- Asset được tra cứu bằng feature-relative path và có fallback khi thiếu.

## Data Flow

1. MenuFile tạo QAction.
2. Action hiển thị icon và shortcut.
3. MainView/ViewModel thực thi nghiệp vụ.

