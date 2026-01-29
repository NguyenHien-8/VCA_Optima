from PyQt6.QtWidgets import QMenu, QStyle
from PyQt6.QtGui import QAction

# Import Dialog mới
from App.Gui.Dialog.MenuBar.ConfigCameraDialog import ConfigCameraDialog

class MenuSetup(QMenu):
    def __init__(self, parent_window):
        super().__init__("Setup", parent_window)
        self.parent_window = parent_window 
        self.setup_actions()

    def setup_actions(self):
        style = self.style()

        # Hardware Connection
        act_hardware = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon), "Hardware Connection", self)
        act_hardware.triggered.connect(self.on_hardware)
        self.addAction(act_hardware)

        # Camera Connection
        act_camera = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DriveDVDIcon), "Camera Connection", self)
        act_camera.triggered.connect(self.on_camera)
        self.addAction(act_camera)

    def on_hardware(self): 
        print("[Setup] Open Hardware Dialog (COM Port)")

    def on_camera(self):
        # Truyền cả camera_manager và parent_window (self.parent_window)
        dialog = ConfigCameraDialog(self.parent_window.camera_manager, self.parent_window)
        
        # Dùng exec() để chặn cửa sổ chính (Modal Dialog)
        dialog.exec()