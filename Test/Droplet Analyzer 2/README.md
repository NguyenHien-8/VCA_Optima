# Test / Droplet Analyzer 2

## Project Overview

Prototype thế hệ hai dùng để đối chiếu một analyzer tự xây dựng với integration pyDSA_core, cùng hai biến thể ImageEditor/ViewModel.

## Annotated Directory Structure

- `DropletAnalyzer_Algorithm.py` — custom robust detector và circle-fit.
- `DropletAnalyzer_pyDSA.py` — adapter thử nghiệm `DropletProfile`, `BaselineDetector`, `ContactAngleCalculator`.
- `DropletAnalyzer.py` — analyzer baseline cũ để so sánh.
- `ImageEditor.py` — UI chọn/chạy analyzer.
- `ImageEditorViewModel.py` và `ImageEditorViewModel copy.py` — điều phối các biến thể.

## Core Algorithms & Implementation

- Custom detector thử tuần tự Adaptive Gaussian, Otsu, Canny và relaxed adaptive; morphology nối vùng rồi chọn contour theo ngưỡng area/circularity.
- Contour được moving-average, baseline lấy từ 10% điểm đáy, contact points là extrema gần baseline; mỗi nửa contour được fit circle bằng hệ moment tuyến tính.
- Góc dùng `acos((yc-y_base)/R)`; fallback fit một circle hoặc xấp xỉ height/width.
- pyDSA branch tạo `DropletProfile`, detect polynomial baseline và circle-fitting contact angles; module ghi lỗi nếu library không khả dụng.
- Production đã thay pipeline này bằng fit ellipse có trọng số và hướng tiếp tuyến inside-liquid.

## Data Flow

1. QPixmap → custom hoặc pyDSA analyzer.
2. Analyzer → contour/baseline/angles/metrics → result object.
3. ViewModel phát result → ImageEditor render và cho phép người dùng so sánh.

