from PyQt6.QtWidgets import QMenu, QStyle
from PyQt6.QtGui import QAction # <--- SỬA DÒNG NÀY

class MenuCalibration(QMenu):
    def __init__(self, parent_window):
        super().__init__("Calibration", parent_window)
        # ... code phía sau giữ nguyên
        self.addAction(QAction("Calibrate Axis", self, triggered=lambda: print("[Calibration] Settings")))