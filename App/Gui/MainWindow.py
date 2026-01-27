from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, 
                             QWidget)
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
        self.connect_signals()
        
        # Tùy chọn: Tự động kết nối camera đầu tiên khi mở app (nếu muốn)
        # self.camera_manager.scan_cameras() 

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- PHẦN HIỂN THỊ CAMERA ---
        # Không còn các nút điều khiển ở đây nữa
        
        self.image_label = QLabel("Vào Menu Setup -> Camera Connection để kết nối.")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #555; background-color: #222; color: #AAA; font-size: 16px;")
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setScaledContents(True) # Cho phép co giãn ảnh
        main_layout.addWidget(self.image_label)

    def connect_signals(self):
        # MainWindow chỉ quan tâm đến việc nhận ảnh để hiển thị
        self.camera_manager.frame_received_signal.connect(self.update_image)
        self.camera_manager.error_occurred_signal.connect(self.show_error)
        
        # Các signal điều khiển (list, status) giờ do CameraDialog lo, 
        # MainWindow không cần lắng nghe nữa (hoặc lắng nghe status để hiện xuống StatusBar nếu có)

    @pyqtSlot(QImage)
    def update_image(self, qt_img):
        self.image_label.setPixmap(QPixmap.fromImage(qt_img))

    @pyqtSlot(str)
    def show_error(self, message):
        self.image_label.setText(f"LỖI: {message}")
        self.image_label.setStyleSheet("border: 2px solid red; background-color: #300; color: #FFF; font-weight: bold;")