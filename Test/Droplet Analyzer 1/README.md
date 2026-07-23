# Test / Droplet Analyzer 1

## Project Overview

Prototype phân tích giọt thế hệ đầu: tự phân đoạn contour, ước lượng đặc trưng hình học và fit đường tròn cục bộ để suy ra contact angle.

## Annotated Directory Structure

- `DropletAnalyzer.py` — pipeline gốc và worker QThread.
- `DropletAnalyzer copy.py` — biến thể nhiều detector, pyDSA fallback và circle fit cải tiến.
- `ImageEditor.py` — UI chạy calibration, hiển thị/export kết quả.
- `ImageEditorViewModel.py` — load/save image, aspect ratio và điều phối analyzer.
- `ImageEditorViewModel copy.py` — ViewModel gắn biến thể analyzer cải tiến.

## Core Algorithms & Implementation

- Pipeline gốc: QPixmap→OpenCV → grayscale/blur/threshold/morphology → contour → properties → baseline gần đáy → tách trái/phải → least-squares circle.
- Góc được lấy từ hình học tâm–bán kính tại baseline; kết quả gồm left/right/average, kích thước, ellipse và thể tích cap ước lượng.
- Bản `copy` thử Adaptive → Otsu → Canny → relaxed threshold, chấm contour bằng area×circularity và dùng pyDSA_core khi khả dụng.
- Đây là lịch sử nghiên cứu; production không gọi trực tiếp các class này.

## Data Flow

1. ImageEditorViewModel nhận QPixmap/aspect ratio.
2. Analyzer phát progress/result/error signals.
3. UI hiển thị overlay, thông số và cho phép export; kết quả thử nghiệm dẫn tới module Analysis hiện tại.

