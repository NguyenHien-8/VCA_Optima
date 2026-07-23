# App/Models/Vision/CameraManager.py
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtGui import QImage
from App.Models.Vision.CameraThread import CameraThread
from App.Models.Vision.HardwareCameraScan import HardwareCameraScan


class CameraManager(QObject):
    frame_received_signal = pyqtSignal(QImage)
    preview_signal = pyqtSignal(QImage)
    camera_list_signal = pyqtSignal(list)
    error_occurred_signal = pyqtSignal(str)
    status_message_signal = pyqtSignal(str)
    fps_updated = pyqtSignal(float)

    MIN_WIDTH, MIN_HEIGHT = 480, 360
    MAX_WIDTH, MAX_HEIGHT = 960, 576
    DEFAULT_WIDTH, DEFAULT_HEIGHT = 640, 480
    MAX_RETRIES = 5

    def __init__(self):
        super().__init__()
        self.current_thread = None
        self.scan_thread = None
        self.active_camera_index = None
        self.resolution = (self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.retry_count = 0
        self._preview_mode = False
        self.current_fps = 30.0
        self._ref_count = 0

        # Cache danh sách camera để lấy tên thật mà không cần mở dialog config
        self.available_cameras = []

        # Tự scan camera ngay sau khi khởi tạo
        QTimer.singleShot(0, self.scan_cameras)

    def set_preview_mode(self, is_preview: bool):
        self._preview_mode = is_preview

    def set_resolution(self, width, height):
        if width < self.MIN_WIDTH or height < self.MIN_HEIGHT:
            self.status_message_signal.emit(f"Resolution too low. Min: {self.MIN_WIDTH}x{self.MIN_HEIGHT}")
            return
        if width > self.MAX_WIDTH or height > self.MAX_HEIGHT:
            self.status_message_signal.emit(f"Resolution too high. Max: {self.MAX_WIDTH}x{self.MAX_HEIGHT}")
            return
        self.resolution = (width, height)
        self.status_message_signal.emit(f"Resolution set to {width}x{height}. Restart camera to apply.")
        if self.active_camera_index is not None:
            self.change_camera(self.active_camera_index)

    def get_camera_name(self, cam_idx):
        for cam in self.available_cameras:
            if isinstance(cam, dict) and cam.get("index") == cam_idx:
                return cam.get("name", f"Camera {cam_idx}")
        return f"Camera {cam_idx}"

    def scan_cameras(self):
        if self.scan_thread is not None and self.scan_thread.isRunning():
            return
        self.status_message_signal.emit("Scanning devices...")
        self.scan_thread = HardwareCameraScan(skip_index=self.active_camera_index)
        self.scan_thread.cameras_found_signal.connect(self._on_scan_finished)
        self.scan_thread.start()

    def change_camera(self, target_cam_idx):
        if target_cam_idx is None:
            self.stop_current_camera()
            self.status_message_signal.emit("Please select a Camera.")
            return

        # Nếu chưa có cache tên camera thì scan trước để StatusBar cập nhật đúng tên
        if not self.available_cameras:
            self.scan_cameras()

        self.retry_count = 0
        self.status_message_signal.emit(f"Connecting Camera {target_cam_idx}...")
        self.stop_current_camera()
        self._start_camera_thread(target_cam_idx)

    def stop_current_camera(self):
        if self.current_thread is not None:
            try:
                self.current_thread.change_pixmap_signal.disconnect()
                self.current_thread.error_signal.disconnect()
                self.current_thread.fps_signal.disconnect()
            except TypeError:
                pass
            self.current_thread.stop_camera()
            self.current_thread.wait()
            self.current_thread.deleteLater()
            self.current_thread = None

    def stop_scan(self):
        """Stop the camera scanning thread if it is currently running."""
        if self.scan_thread is not None and self.scan_thread.isRunning():
            self.scan_thread.quit()
            self.scan_thread.wait()
            self.scan_thread = None

    def cleanup(self):
        """Clean up all camera resources (stop running cameras and scan threads)."""
        self.stop_current_camera()
        self.stop_scan()

    def _start_camera_thread(self, cam_idx):
        self.active_camera_index = cam_idx
        self.current_thread = CameraThread(cam_idx, resolution=self.resolution)
        self.current_thread.change_pixmap_signal.connect(self._on_frame_routed)
        self.current_thread.error_signal.connect(self._on_camera_error_internal)
        self.current_thread.fps_signal.connect(self._on_fps_updated)
        self.current_thread.start()

    @pyqtSlot(float)
    def _on_fps_updated(self, fps):
        self.current_fps = fps
        self.fps_updated.emit(fps)

    @pyqtSlot(list)
    def _on_scan_finished(self, new_cameras):
        self.scan_thread = None

        try:
            new_cameras.sort(key=lambda x: x['index'])
        except Exception as e:
            print(f"Error sorting cameras: {e}")

        self.available_cameras = new_cameras
        self.camera_list_signal.emit(new_cameras)

        if self.active_camera_index is not None:
            found_indices = [cam['index'] for cam in new_cameras if isinstance(cam, dict)]
            if self.active_camera_index not in found_indices:
                lost_idx = self.active_camera_index
                self.status_message_signal.emit(f"Camera {lost_idx} disconnected.")
                self.stop_current_camera()
                self.active_camera_index = None
                self.error_occurred_signal.emit(f"Lost connection to Camera {lost_idx}")

    @pyqtSlot(QImage)
    def _on_frame_routed(self, image):
        if self.retry_count > 0:
            self.retry_count = 0

        if self._preview_mode:
            self.preview_signal.emit(image)
        else:
            self.frame_received_signal.emit(image)

    @pyqtSlot(str)
    def _on_camera_error_internal(self, message):
        self.error_occurred_signal.emit(message)
        self.retry_count += 1

        if self.retry_count > self.MAX_RETRIES:
            self.status_message_signal.emit("Max retries reached. Stopping auto-scan.")
            self.stop_current_camera()
            self.active_camera_index = None
            return

        self.status_message_signal.emit(f"Retry attempt {self.retry_count}/{self.MAX_RETRIES}...")
        target_idx = self.active_camera_index
        self.stop_current_camera()
        self.active_camera_index = target_idx
        QTimer.singleShot(1000, lambda: self._start_camera_thread(target_idx))

    def get_fps(self):
        return self.current_fps

    def ensure_connected(self, cam_index=None):
        """Ensure the camera is connected to the given index (or active index)."""
        if cam_index is None:
            cam_index = self.active_camera_index

        if cam_index is None:
            self.status_message_signal.emit("No camera selected.")
            return

        if not self.available_cameras:
            self.scan_cameras()

        if self.current_thread is not None and self.active_camera_index == cam_index:
            return

        if self.current_thread is not None:
            self.stop_current_camera()

        self.change_camera(cam_index)

    def acquire(self):
        """Increment the reference counter. If it increases from 0 to 1, connect the camera."""
        self._ref_count += 1
        self.status_message_signal.emit(f"Camera acquired. Ref count: {self._ref_count}")

        if not self.available_cameras:
            self.scan_cameras()

        if self._ref_count == 1:
            self.ensure_connected()

    def release(self):
        """Decrease the reference counter. If it reaches 0, disconnect the camera."""
        if self._ref_count > 0:
            self._ref_count -= 1
            self.status_message_signal.emit(f"Camera released. Ref count: {self._ref_count}")
            if self._ref_count == 0:
                self.stop_current_camera()
        else:
            print("ERROR: release() call when ref_count = 0")