# Document / Example Project / VatLieuA

## Project Overview

Project mẫu `VatLieuA` theo schema filesystem của VCA Optima. `config.json` là marker để `ProjectManager` công nhận project.

## Annotated Directory Structure

- `ChatLong1/` — thư mục con trong dataset mẫu.
- `ChatLong2/` — thư mục con trong dataset mẫu.
- File hiện có (1): `config.json`.

## Core Algorithms & Implementation

- `is_folder_project()` kiểm tra sự tồn tại của `config.json`; nội dung mẫu hiện là object JSON rỗng.
- Khi mở, `_scan_project_items()` chỉ nhận thư mục con có đủ `Image/` và `Video/`.
- ProjectManager giữ mapping tên→đường dẫn và trạng thái `SAVED`/`TEMP`; dataset dưới Document được mở như dữ liệu đã lưu.

## Data Flow

1. User chọn thư mục project → validate `config.json`.
2. Manager quét Item hợp lệ → MainViewModel phát signal thêm project/item.
3. Sidebar theo dõi media của từng Item; editors đọc/ghi trong cây này.

