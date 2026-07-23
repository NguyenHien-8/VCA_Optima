# Document / Example Project / Test2

## Project Overview

Project mẫu `Test2` theo schema filesystem của VCA Optima. `config.json` là marker để `ProjectManager` công nhận project.

## Annotated Directory Structure

- `dfndnnd/` — thư mục con trong dataset mẫu.
- `FGSDF/` — thư mục con trong dataset mẫu.
- `HNJGDJHG/` — thư mục con trong dataset mẫu.
- `JKYJJ/` — thư mục con trong dataset mẫu.
- `JRFJTJ/` — thư mục con trong dataset mẫu.
- `jtettrhf/` — thư mục con trong dataset mẫu.
- `JTRJTRJ/` — thư mục con trong dataset mẫu.
- `jyjyjty/` — thư mục con trong dataset mẫu.
- `KJJYKYJK/` — thư mục con trong dataset mẫu.
- `SDFGHSDF/` — thư mục con trong dataset mẫu.
- File hiện có (1): `config.json`.

## Core Algorithms & Implementation

- `is_folder_project()` kiểm tra sự tồn tại của `config.json`; nội dung mẫu hiện là object JSON rỗng.
- Khi mở, `_scan_project_items()` chỉ nhận thư mục con có đủ `Image/` và `Video/`.
- ProjectManager giữ mapping tên→đường dẫn và trạng thái `SAVED`/`TEMP`; dataset dưới Document được mở như dữ liệu đã lưu.

## Data Flow

1. User chọn thư mục project → validate `config.json`.
2. Manager quét Item hợp lệ → MainViewModel phát signal thêm project/item.
3. Sidebar theo dõi media của từng Item; editors đọc/ghi trong cây này.

