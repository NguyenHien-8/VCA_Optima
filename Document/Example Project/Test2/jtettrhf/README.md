# Document / Example Project / Test2 / jtettrhf

## Project Overview

Item mẫu `jtettrhf` thuộc project `Test2`. Item là đơn vị lưu một phiên/chất lỏng với hai kho media bắt buộc.

## Annotated Directory Structure

- `Image/` — thư mục con chứa ảnh.
- `Video/` — thư mục con chứa video.
- File hiện có (1): `jtettrhf.tnh`.

## Core Algorithms & Implementation

- `is_folder_item()` yêu cầu chính thư mục này cùng hai directory `Image/` và `Video/`.
- File `.tnh` nếu có chỉ là marker/nội dung cấu hình thử nghiệm; Release 1.1.0 không dùng nó để validate Item.
- Copy/move Item dùng `shutil.copytree`; khi trùng tên, hậu tố `_CopyN` được tăng cho tới khi có đường dẫn trống.

## Data Flow

1. Project scan tìm Item này và thêm node vào sidebar.
2. Camera editor chọn Item làm storage target → ảnh/video được ghi vào hai thư mục con.
3. Image/Video editor đọc media; analysis result quay lại `Image/`.

