# App/Presentation/Views/Widgets/MenuBar/MenuSetup.py
from PyQt6.QtWidgets import QMenu, QStyle
from PyQt6.QtGui import QAction

class MenuSetup(QMenu):
    def __init__(self, parent_window):
        super().__init__("Setup", parent_window)
        self.parent_window = parent_window 
        self.setup_actions()

    def setup_actions(self):
        style = self.style()

        # Hardware Connection
        act_hardware = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon), "Hardware Configuration", self)
        act_hardware.triggered.connect(self.on_hardware)
        self.addAction(act_hardware)

        # Camera Connection
        act_camera = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DriveDVDIcon), "Camera Connection", self)
        act_camera.triggered.connect(self.on_camera)
        self.addAction(act_camera)

    def on_hardware(self):
        from App.Presentation.Views.Dialog.ConfigHardwareDialog import ConfigHardwareDialog

        # Lấy hardware_manager từ view_model của MainView
        hardware_manager = self.parent_window.view_model.hardware_manager
        dialog = ConfigHardwareDialog(hardware_manager, self.parent_window)
        dialog.exec()

    def on_camera(self):
        from App.Presentation.Views.Dialog.ConfigCameraDialog import ConfigCameraDialog

        # Lấy camera_manager từ view_model của MainView
        camera_manager = self.parent_window.view_model.camera_manager
        dialog = ConfigCameraDialog(camera_manager, self.parent_window)
        dialog.exec()
