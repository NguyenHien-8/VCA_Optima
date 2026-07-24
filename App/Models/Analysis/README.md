# App / Models / Analysis

## Project Overview

Module thuật toán production để xác định baseline, fit biên giọt và tính hai góc tiếp xúc bên trong pha lỏng.

## Annotated Directory Structure

- `AnalysisManager.py` — facade chọn baseline/fitting method.
- `BaselineAnalysis.py` — tạo phương trình đường thẳng từ hai điểm; mirror method là TODO.
- `DropletAnalysis.py` — Fitzgibbon fit, robust weighted least-squares, contact geometry và auto edge detection bị ràng buộc bởi baseline.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Fitzgibbon: lập design matrix `[x²,xy,y²,x,y,1]`, giải generalized eigenproblem, lọc ellipse bằng `4AC-B²>0`, đổi conic sang `(x0,y0,a,b,theta)`.
- Ellipse refinement: residual đại số chia chuẩn gradient (Sampson-like), trọng số `exp(-alpha*d_norm²)` ưu tiên vùng gần baseline, SciPy `least_squares` với `soft_l1`.
- Circle branch: tối ưu radial residual cho `(x0,y0,R)`; tên UI là Young-Laplace nhưng implementation chỉ là xấp xỉ đường tròn.
- Contact angle: giải giao tuyến đường thẳng–ellipse/circle, sắp tiếp điểm trái/phải, định hướng baseline vào footprint và chọn tiếp tuyến theo nhánh curve phía chất lỏng để tránh lỗi `theta` so với `180-theta`.
- Auto edge chỉ chạy khi đã có baseline `(a,b,c)`. Ảnh được đổi về grayscale `uint8`, blur Gaussian và ánh xạ chính xác giữa pixel với miền vật lý 5 mm × 3 mm.
- Baseline tạo một half-plane mask `y > y_baseline(x)` trước threshold; toàn bộ substrate, bóng phản chiếu và nhiễu phía dưới bị loại khỏi ảnh nhị phân ngay từ đầu.
- Sau Otsu inverse và morphology thích nghi theo kích thước ảnh, contour ứng viên phải đạt diện tích tối thiểu, độ cao cap tối thiểu và có một cung liên tục nằm cách baseline ít nhất hai pixel.
- Cung hợp lệ dài nhất được chọn theo arc length và cap height. Clearance profile từ contact trái qua apex tới contact phải được dùng để cắt hai substrate tail có độ cao thấp, tránh contour lan ngang ra ngoài footprint.
- Hai baseline anchor được dùng như contact hints khi chúng đủ gần contact tự động. Hint ở xa contour bị bỏ qua; fallback sẽ fit cục bộ cạnh trái/phải theo clearance rồi ngoại suy tới sát baseline.
- Liquid-cap arc sau khi khôi phục hai contact endpoint được resample theo khoảng cách cung thay vì theo chỉ số contour. Bước kiểm tra cuối chỉ trả các điểm thỏa `y_point > y_baseline(x_point)`.

## Data Flow

1. Hai baseline points → `BaselineAnalyzer` → coefficients `(a,b,c)`; hai điểm gốc tiếp tục được giữ làm contact hints.
2. Grayscale image + baseline coefficients → half-plane mask → Otsu/morphology → contour candidates.
3. Longest valid arc → clearance-tail trimming → validate contact hints hoặc local-side extrapolation.
4. Liquid-cap arc cùng hai contact endpoints → uniform arc-length sampling → edge points phía trên baseline.
5. Edge points + baseline coefficients đi vào ellipse/circle fit; baseline cũng được dùng để tính giao tuyến và tạo trọng số fit.
6. Kết quả gồm góc, tiếp điểm, tiếp tuyến → `DropletAnalysisWindow` vẽ overlay/lưu ảnh.
