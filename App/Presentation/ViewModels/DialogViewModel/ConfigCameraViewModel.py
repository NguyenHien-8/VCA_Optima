# App/Presentation/ViewModels/DialogViewModel/ConfigCameraViewModel.py
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage
from App.Models.CamHardwareManager import CameraConfigBackend

class ConfigCameraViewModel(QObject):
    camera_list_updated = pyqtSignal(list)
    preview_frame_received = pyqtSignal(QImage)

    def __init__(self, camera_manager):
        super().__init__()
        self.backend = CameraConfigBackend(camera_manager)
        self._connect_signals()

    def _connect_signals(self):
        self.backend.camera_manager.camera_list_signal.connect(self.camera_list_updated)
        self.backend.camera_manager.preview_signal.connect(self.preview_frame_received)

    def scan_cameras(self):
        self.backend.scan_cameras()

    def set_selected_camera(self, index):
        self.backend.set_selected_camera(index)

    def get_selected_camera(self):
        return self.backend.get_selected_camera()
    
    def get_original_camera_id(self):     
        return self.backend.original_camera_id

    def connect_preview(self, cam_idx):
        self.backend.connect_preview(cam_idx)

    def stop_preview(self):
        self.backend.stop_preview()

    def apply_changes(self, connect_now=False):
        self.backend.apply_changes(connect_now)

    def revert_changes(self):
        self.backend.revert_changes()