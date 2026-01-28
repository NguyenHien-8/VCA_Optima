from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap

from App.Gui.MenuBar import MenuBar
from Vision.CameraManager import CameraManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TNH Optima")
        self.resize(1000, 700)
        
        # --- MENU BAR ---
        self.menu_bar_manager = MenuBar(self)
        self.setMenuBar(self.menu_bar_manager)

        # --- LOGIC ---
        self.camera_manager = CameraManager()
        
        self.setup_ui()
        
        # Kết nối tín hiệu mặc định ban đầu
        self.connect_signals()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Màn hình chính ---
        self.image_label = QLabel("Waiting for Camera...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #B0B0B0; background-color: #C8C8C8; color: #333333; font-size: 25px;")
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setScaledContents(True) 
        main_layout.addWidget(self.image_label)

    def connect_signals(self):
        # Kết nối tín hiệu nhận ảnh vào hàm update_image của Main Window
        self.camera_manager.frame_received_signal.connect(self.update_image)
        self.camera_manager.error_occurred_signal.connect(self.show_error)

    @pyqtSlot(QImage)
    def update_image(self, qt_img):
        # Hàm này chỉ chạy khi CameraDialog đã Apply và kết nối lại signal
        self.image_label.setPixmap(QPixmap.fromImage(qt_img))

    @pyqtSlot(str)
    def show_error(self, message):
        # Chỉ hiện lỗi nếu không phải đang ở trong Dialog Setting
        self.image_label.setText(f"LỖI: {message}")