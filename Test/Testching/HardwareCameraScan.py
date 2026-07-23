import sys
import cv2
from PyQt6.QtCore import QThread, pyqtSignal

class HardwareCameraScan(QThread):
    cameras_found_signal = pyqtSignal(list)

    def __init__(self, skip_index=None):
        super().__init__()
        self.skip_index = skip_index

    def run(self):
        available_cameras = []
        for i in range(2):
            # Nếu camera này đang được bật bởi User -> Coi như nó tồn tại
            if self.skip_index is not None and i == self.skip_index:
                available_cameras.append(i)
                continue

            # Kiểm tra các camera khác
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