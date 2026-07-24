# App / Presentation / Views / Widgets

## Project Overview

Các widget tái sử dụng cho cây project, tab editor, trạng thái và phân tích giọt.

## Annotated Directory Structure

- `SideBar.py` — cây Project/Item/Image/Video, explicit media update và filesystem watcher.
- `EditorWorkspace.py` — tab container, drag/drop và close contract.
- `DropletAnalysisWindow.py` — tương tác điểm, fit, overlay và export.
- `StatusBar.py` — trạng thái camera/serial.
- `FileEditorWorkspace/` — camera, image/video editor và control widgets.
- `MenuBar/` — menu actions, shortcuts và sidebar toggle.

## Core Algorithms & Implementation

- SideBar lazy-scan media bằng worker và chèn kết quả theo batch 200 item.
- Tối đa hai media scanner chạy đồng thời; các yêu cầu còn lại nằm trong queue để project lớn không tạo quá nhiều `QThread`.
- Node `Image/Video` được dò nền ngay khi Item xuất hiện: có media thì policy là `ShowIndicator`, rỗng thì `DontShowIndicatorWhenChildless`.
- Custom branch renderer xét cả child đã load và `ChildIndicatorPolicy`, nên mũi tên xuất hiện trước lần click đầu tiên.
- `notify_media_created` validate full path, chống duplicate, chèn theo thứ tự và tự mở đúng Project/Item/Image|Video node.
- Nếu watcher phát thay đổi khi scanner đang chạy, refresh được đưa vào pending set và chạy lại sau `finished`.
- Watcher vẫn xử lý file tạo/xóa từ ứng dụng ngoài.
- Widget có worker phát `close_ready` để tránh xóa QThread còn chạy.
- Droplet Auto Detect yêu cầu người dùng xác định baseline trước khi chạy. Worker truyền một bản sao bất biến của coefficients vào model để cô lập substrate/reflection và chỉ lấy cung biên giọt phía trên baseline.
- Điểm biên trả về được lấy mẫu đều theo arc length; UI chỉ cập nhật overlay sau khi worker hoàn tất và báo chủ động nếu chưa có baseline hoặc không tìm thấy biên hợp lệ.

## Data Flow

1. Project signals tạo Item → enqueue scan nền cho `Image` và `Video`.
2. Scan result → cache tên file + cập nhật branch indicator, vẫn chưa tạo child khi node đang đóng.
3. Click mở node → render ngay từ cache; danh sách lớn được chèn theo batch.
4. Capture/record thành công → explicit `media_created` → cập nhật SideBar ngay.
5. Filesystem change bên ngoài → watcher → background rescan → indicator/tree update.
6. Double click/drag-drop file → MainView mở editor tương ứng.
7. Droplet baseline → Auto Detect worker → baseline-constrained contour → edge points hợp lệ → UI thread vẽ overlay.
