# App/Presentation/Views/Widgets/MenuBar/MenuCalibration.py
from PyQt6.QtWidgets import QMenu, QStyle
from PyQt6.QtGui import QAction

class MenuCalibration(QMenu):
    def __init__(self, parent_window):
        super().__init__("Calibration", parent_window)
        self.addAction(QAction("Calibrate Axis", self, triggered=lambda: print("[Calibration] Settings")))