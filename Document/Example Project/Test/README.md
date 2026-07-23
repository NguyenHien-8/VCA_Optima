# Document / Example Project / Test

## Project Overview

Tập file Gerber dùng làm dữ liệu tham chiếu ngoài schema Project/Item của VCA Optima.

## Annotated Directory Structure

- Các lớp PCB `F_Cu`, `B_Cu`, `F_Mask` và `Edge_Cuts` ở định dạng `.gbr`.
- Không có `config.json`, `Image/` hay `Video/`.

## Core Algorithms & Implementation

- VCA Optima không có parser Gerber trong Release 1.1.0.
- Thư mục này sẽ không được `ProjectManager` nhận là project hợp lệ nếu mở trực tiếp.

## Data Flow

1. File Gerber chỉ phục vụ tham chiếu.
2. Không đi vào luồng camera/media/contact-angle.
3. Muốn hỗ trợ cần parser/importer mới ngoài scope hiện tại.

