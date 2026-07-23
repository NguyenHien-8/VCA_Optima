# App/Models/Vision/CameraFrameDispatcher.py
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtGui import QImage


class CameraFrameDispatcher(QObject):
    def __init__(self, camera_manager):
        super().__init__()
        self._camera_manager = camera_manager
        self._active_view_model = None
        self._last_frame = None

        self._camera_manager.frame_received_signal.connect(self._on_camera_frame)

    @pyqtSlot(QImage)
    def _on_camera_frame(self, qimage: QImage):
        self._last_frame = qimage
        if self._active_view_model is not None:
            self._active_view_model.receive_frame(qimage)

    def set_active_view_model(self, view_model):
        self._active_view_model = view_model
        if self._active_view_model is not None and self._last_frame is not None:
            self._active_view_model.receive_frame(self._last_frame)