# App / Presentation / Views / Widgets

## Project Overview

Các widget tái sử dụng cho cây project, tab editor, trạng thái và phân tích giọt.

## Annotated Directory Structure

- `SideBar.py` — cây Project/Item/Image/Video, reorder drag-drop, explicit media update và filesystem watcher.
- `EditorWorkspace.py` — tab container, drag/drop và close contract.
- `DropletAnalysisWindow.py` — tương tác điểm, drag-select Measure Point, fit, overlay và export.
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
- Drag-and-drop nội bộ dùng MIME `application/x-tnh-optima-sidebar-node`; Project chỉ reorder ở top-level, Item chỉ reorder trong cùng Project. Drop sang Project khác hoặc lên Image/Video/file sai cấp bị từ chối để không vô tình thay đổi filesystem.
- Reorder dùng `takeTopLevelItem`/`takeChild` rồi chèn lại chính object cũ, nhờ đó selection, expanded state, media cache và watcher không phải dựng lại.
- Widget có worker phát `close_ready` để tránh xóa QThread còn chạy.
- Droplet Auto Detect yêu cầu người dùng xác định baseline trước khi chạy. Worker truyền bản sao bất biến của coefficients và hai baseline anchors vào model để cô lập substrate/reflection, xác định footprint và chỉ lấy cung biên giọt phía trên baseline.
- Baseline anchors chỉ neo hai contact endpoint khi nằm đủ gần biên tự động; model tự fallback sang contact extrapolation nếu hint không phù hợp.
- Điểm biên trả về đã loại substrate tails và được lấy mẫu đều theo arc length; UI chỉ cập nhật overlay sau khi worker hoàn tất và báo chủ động nếu chưa có baseline hoặc không tìm thấy biên hợp lệ.
- Measure Point selection phân biệt click và drag bằng ngưỡng pixel nhỏ: click vùng trống thêm point, drag vùng trống vẽ rectangle, các point nằm trong rectangle được render màu đen và lưu bằng `selected_measurement_indices`.
- Context menu chuột phải trong Measure Point chỉ mở khi có selection hợp lệ; action `Delete` xóa đúng các index được chọn, clear rectangle/selection và render lại danh sách point còn lại. Nút `Delete Measure Point` vẫn xóa tất cả khi không có selection.
- `DropletAnalysisWindow` là top-level window độc lập: MainView chỉ là logical owner dùng để điều phối minimize, còn Win32 taskbar style cho phép Windows tạo thumbnail riêng trong cùng nhóm TNH Optima thay vì caption thu nhỏ trên desktop.
- `WA_DeleteOnClose` bảo đảm analysis object ẩn không bị giữ lại; source image path được truyền riêng nên việc đổi QObject owner không ảnh hưởng vị trí lưu kết quả.

## Data Flow

1. Project signals tạo Item → enqueue scan nền cho `Image` và `Video`.
2. Scan result → cache tên file + cập nhật branch indicator, vẫn chưa tạo child khi node đang đóng.
3. Click mở node → render ngay từ cache; danh sách lớn được chèn theo batch.
4. Capture/record thành công → explicit `media_created` → cập nhật SideBar ngay.
5. Filesystem change bên ngoài → watcher → background rescan → indicator/tree update.
6. Drag Project/Item → validate node kind + parent boundary → tính index trước/sau → di chuyển nguyên tree item.
7. Double click/drag-drop file → MainView mở editor tương ứng.
8. Droplet baseline coefficients + anchors → Auto Detect worker → liquid-cap contour + validated contacts → edge points hợp lệ → UI thread vẽ overlay.
9. Measure Point drag-select → selected indices → chuột phải `Delete` → xóa selected points → redraw measurement overlay.
10. ImageEditor mở Droplet Analysis → truyền source path + MainView logical owner → helper đăng ký window/taskbar style → grouped preview; close phát `destroyed` để gỡ khỏi danh sách cửa sổ.
