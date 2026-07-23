# App / Models / Analysis

## Project Overview

Module thuật toán production để xác định baseline, fit biên giọt và tính hai góc tiếp xúc bên trong pha lỏng.

## Annotated Directory Structure

- `AnalysisManager.py` — facade chọn baseline/fitting method.
- `BaselineAnalysis.py` — tạo phương trình đường thẳng từ hai điểm; mirror method là TODO.
- `DropletAnalysis.py` — Fitzgibbon fit, robust weighted least-squares, contact geometry và auto edge detection.
- `__init__.py` — package marker.

## Core Algorithms & Implementation

- Fitzgibbon: lập design matrix `[x²,xy,y²,x,y,1]`, giải generalized eigenproblem, lọc ellipse bằng `4AC-B²>0`, đổi conic sang `(x0,y0,a,b,theta)`.
- Ellipse refinement: residual đại số chia chuẩn gradient (Sampson-like), trọng số `exp(-alpha*d_norm²)` ưu tiên vùng gần baseline, SciPy `least_squares` với `soft_l1`.
- Circle branch: tối ưu radial residual cho `(x0,y0,R)`; tên UI là Young-Laplace nhưng implementation chỉ là xấp xỉ đường tròn.
- Contact angle: giải giao tuyến đường thẳng–ellipse/circle, sắp tiếp điểm trái/phải, định hướng baseline vào footprint và chọn tiếp tuyến theo nhánh curve phía chất lỏng để tránh lỗi `theta` so với `180-theta`.
- Auto edge: blur → Otsu inverse → morphology close → contour lớn nhất → bỏ đáy → sample đều → đổi sang 5 mm × 3 mm.

## Data Flow

1. Grayscale image và profile points đi vào `AnalysisManager`.
2. Baseline coefficients được dùng cả để tính giao tuyến và tạo trọng số fit.
3. Kết quả gồm góc, tiếp điểm, tiếp tuyến → `DropletAnalysisWindow` vẽ overlay/lưu ảnh.

