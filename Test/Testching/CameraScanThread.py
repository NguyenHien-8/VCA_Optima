import sys
import cv2
from PyQt6.QtCore import QThread, pyqtSignal

class CameraScanThread(QThread):
    """
    Thread quét các cổng camera khả dụng.
    Cập nhật logic: Bỏ qua kiểm tra vật lý đối với camera đang active để tránh xung đột resource.
    """
    cameras_found_signal = pyqtSignal(list)

    def __init__(self, active_index=None):
        super().__init__()
        self.active_index = active_index  # Index camera đang chạy (nếu có)

    def run(self):
        available_cameras = []
        # Quét 3 index đầu tiên (có thể tăng range(10) nếu máy nhiều cam)
        for i in range(3):
            # LOGIC QUAN TRỌNG:
            # Nếu i là camera đang chạy, ta mặc định nó tồn tại và add vào luôn.
            # Không cố mở lại bằng cv2.VideoCapture vì sẽ gây xung đột (Device Busy).
            if self.active_index is not None and i == self.active_index:
                available_cameras.append(i)
                continue

            # Các camera khác thì kiểm tra bình thường
            if sys.platform.startswith("win"):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(i)
                
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
        
        self.cameras_found_signal.emit(available_cameras)