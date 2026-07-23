# Test

## Project Overview

Kho prototype và thử nghiệm thủ công hình thành trước/bên cạnh implementation trong `App/`. Đây không phải test suite tự động: không có fixture/assertion/runner; nhiều file chứa import path cũ và không nên được xem là entry point production.

## Annotated Directory Structure

- `Droplet Analyzer 1/` — thế hệ contour/circle-fit đầu tiên và biến thể fallback.
- `Droplet Analyzer 2/` — so sánh custom robust algorithm với pyDSA_core.
- `Run Stable/` — snapshot camera UI từng chạy ổn định.
- `Source Code chưa có Droplet Analysis/` — image editor trước khi gắn tính năng phân tích.
- `Testching/` — thử nghiệm sidebar, file editor, camera và menu.
- `Water Droplet Analysis Research Project/` — placeholder nghiên cứu.

## Core Algorithms & Implementation

- Prototype được giữ để truy vết quyết định thiết kế và so sánh cách phát hiện/fit.
- Thuật toán production hiện nằm ở `App/Models/Analysis`, đã chuyển sang baseline tương tác + ellipse/circle robust fit.
- Không nên import các file ở đây vào production vì nhiều module trỏ tới package `Src` cũ hoặc copy trùng lặp.

## Data Flow

1. Developer chạy từng prototype thủ công với dữ liệu ảnh/camera.
2. Kết quả thử nghiệm được dùng để điều chỉnh UI/algorithm.
3. Phần đã ổn định được tái cấu trúc vào `App/`; thư mục Test không tham gia runtime chuẩn.

