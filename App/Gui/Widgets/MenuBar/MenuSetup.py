from PyQt6.QtWidgets import QMenu, QStyle
from PyQt6.QtGui import QAction

# Import Dialog mới
from App.Gui.Widgets.CameraDialog import CameraDialog

class MenuSetup(QMenu):
    def __init__(self, parent_window):
        super().__init__("Setup", parent_window)
        self.parent_window = parent_window # parent_window chính là MainWindow
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
        # Tạo và hiển thị Dialog
        # Truyền camera_manager từ MainWindow vào Dialog để nó điều khiển
        dialog = CameraDialog(self.parent_window.camera_manager, self.parent_window)
        
        # Dùng dialog.exec() nếu muốn chặn thao tác Main khi đang mở setting
        # Hoặc dialog.show() nếu muốn vừa mở setting vừa xem Main
        dialog.exec()