# File: Ver1.1/Vision/CameraManager.py
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage

# --- SỬA ĐỔI IMPORT ---
from Vision.CameraThread import CameraThread
from Vision.HardwareCameraScan import HardwareCameraScan
# ----------------------

class CameraManager(QObject):
    frame_received_signal = pyqtSignal(QImage)
    camera_list_signal = pyqtSignal(list)
    error_occurred_signal = pyqtSignal(str)
    status_message_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_thread = None
        self.scan_thread = None
        self.active_camera_index = None 

    def set_paused(self, paused: bool):
        if self.current_thread is not None:
            self.current_thread.set_paused(paused)
            status = "Tạm dừng" if paused else "Đang chạy"
            self.status_message_signal.emit(f"Camera {self.active_camera_index}: {status}")

    def scan_cameras(self):
        if self.scan_thread is not None and self.scan_thread.isRunning():
            return

        self.status_message_signal.emit("Đang quét thiết bị...")
        self.scan_thread = HardwareCameraScan(skip_index=self.active_camera_index)
        self.scan_thread.cameras_found_signal.connect(self._on_scan_finished)
        self.scan_thread.start()

    def _on_scan_finished(self, new_cameras):
        new_cameras.sort()
        self.camera_list_signal.emit(new_cameras)
        if not new_cameras:
            self.status_message_signal.emit("Không tìm thấy Camera nào.")
        elif self.active_camera_index is None:
            self.status_message_signal.emit(f"Tìm thấy {len(new_cameras)} thiết bị.")

    def change_camera(self, target_cam_idx):
        if target_cam_idx is None:
            self.stop_current_camera()
            self.status_message_signal.emit("Vui lòng chọn Camera.")
            return

        if self.active_camera_index == target_cam_idx:
            return

        self.status_message_signal.emit(f"Đang kết nối Camera {target_cam_idx}...")
        self.stop_current_camera()
        self._start_camera_thread(target_cam_idx)

    def stop_current_camera(self):
        if self.current_thread is not None:
            try:
                self.current_thread.change_pixmap_signal.disconnect()
                self.current_thread.error_signal.disconnect()
            except: pass
            
            self.current_thread.stop_camera()
            self.current_thread.wait()
            self.current_thread = None
        
        self.active_camera_index = None

    def _start_camera_thread(self, cam_idx):
        self.active_camera_index = cam_idx 
        self.current_thread = CameraThread(cam_idx)
        self.current_thread.change_pixmap_signal.connect(self.frame_received_signal.emit)
        self.current_thread.error_signal.connect(self._on_camera_error_internal)
        self.current_thread.start()

    @pyqtSlot(str)
    def _on_camera_error_internal(self, message):
        self.stop_current_camera()
        self.error_occurred_signal.emit(message)
        self.scan_cameras()

    def stop_all(self):
        self.stop_current_camera()