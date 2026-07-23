# App/Models/Vision/CameraThread.py
import sys
import cv2
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from PyQt6.QtGui import QImage

class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    error_signal = pyqtSignal(str)
    fps_signal = pyqtSignal(float)

    def __init__(self, camera_index=0, resolution=(640, 480)):
        super().__init__()
        self.camera_index = camera_index
        self.resolution = resolution
        self._is_running = True
        self._is_paused = False
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()
        self.fps = 30.0 

    def stop_camera(self):
        self.mutex.lock()
        self._is_running = False
        self.wait_condition.wakeAll()
        self.mutex.unlock()
        self.quit()
        self.wait()

    def set_paused(self, state: bool):
        self.mutex.lock()
        self._is_paused = state
        if not state:
            self.wait_condition.wakeAll()
        self.mutex.unlock()

    def run(self):
        if sys.platform.startswith("win"):
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(self.camera_index)

        width, height = self.resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if not cap.isOpened():
            self.error_signal.emit(f"Failed to open camera {self.camera_index}")
            return

        # --- Get actual FPS from the camera ---
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps is None or fps <= 0:
            fps = 30.0
        self.fps = fps
        self.fps_signal.emit(self.fps)

        while True:
            self.mutex.lock()
            if not self._is_running:
                self.mutex.unlock()
                break

            if self._is_paused:
                self.wait_condition.wait(self.mutex)
                self.mutex.unlock()
                continue
            self.mutex.unlock()

            ret, cv_img = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                p_image = convert_to_qt_format.copy()
                self.change_pixmap_signal.emit(p_image)
            else:
                self.error_signal.emit(f"Lost signal from Camera {self.camera_index}")
                break

        cap.release()