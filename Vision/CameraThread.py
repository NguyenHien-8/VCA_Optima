# File: Ver1.1/Vision/CameraThread.py
import sys
import cv2
import time
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    error_signal = pyqtSignal(str) 

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self._is_running = True
        self._is_paused = False

    def stop_camera(self):
        self._is_running = False
        self.quit()
        self.wait()

    def set_paused(self, state: bool):
        self._is_paused = state

    def run(self):
        if sys.platform.startswith("win"):
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(self.camera_index)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            self.error_signal.emit(f"Không thể mở Camera {self.camera_index}")
            return

        while self._is_running:
            ret, cv_img = cap.read()

            if ret:
                if self._is_paused:
                    time.sleep(0.05)
                    continue 

                rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.change_pixmap_signal.emit(convert_to_qt_format)
            else:
                self.error_signal.emit(f"Mất tín hiệu Camera {self.camera_index}")
                self._is_running = False
                break
        
        cap.release()