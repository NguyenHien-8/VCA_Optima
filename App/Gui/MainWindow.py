# File: Ver1.1/App/Gui/MainWindow.py
from PyQt6.QtWidgets import (QMainWindow, QLabel, QComboBox, 
                             QVBoxLayout, QWidget, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap

# --- SỬA ĐỔI IMPORT ---
from Vision.CameraManager import CameraManager
# ----------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TNH Optima")
        self.resize(800, 600)
        
        self.camera_manager = CameraManager()
        self.is_paused = False 
        
        self.setup_ui()
        self.connect_signals()
        
        # Quét lần đầu
        self.camera_manager.scan_cameras()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Controls Area
        control_layout = QHBoxLayout()
        
        self.camera_selector = QComboBox()
        self.camera_selector.setMinimumWidth(200)
        self.camera_selector.addItem("--- Chọn Camera ---", None)
        self.camera_selector.currentIndexChanged.connect(self.on_user_select_camera)
        control_layout.addWidget(self.camera_selector)

        self.btn_refresh = QPushButton("Làm mới")
        self.btn_refresh.clicked.connect(self.on_click_refresh)
        control_layout.addWidget(self.btn_refresh)

        self.btn_pause = QPushButton("Tạm dừng")
        self.btn_pause.setCheckable(True)
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.on_click_pause)
        control_layout.addWidget(self.btn_pause)
        
        main_layout.addLayout(control_layout)

        # Display Area
        self.image_label = QLabel("Vui lòng chọn Camera")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #555; background-color: #222; color: #AAA; font-size: 16px;")
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setScaledContents(True) 
        main_layout.addWidget(self.image_label)

    def connect_signals(self):
        self.camera_manager.frame_received_signal.connect(self.update_image)
        self.camera_manager.camera_list_signal.connect(self.update_camera_list)
        self.camera_manager.error_occurred_signal.connect(self.show_error)
        self.camera_manager.status_message_signal.connect(self.update_status_text)

    def on_click_pause(self):
        if self.btn_pause.isChecked():
            self.camera_manager.set_paused(True)
            self.btn_pause.setText("Tiếp tục")
            self.image_label.setStyleSheet("border: 2px solid yellow; background-color: #222;")
        else:
            self.camera_manager.set_paused(False)
            self.btn_pause.setText("Tạm dừng")
            self.image_label.setStyleSheet("border: 2px solid #555; background-color: #222;")

    def on_click_refresh(self):
        self.camera_selector.setEnabled(False)
        self.btn_refresh.setEnabled(False)
        self.camera_manager.scan_cameras()

    @pyqtSlot(list)
    def update_camera_list(self, cameras):
        current_cam_idx = self.camera_selector.currentData()
        
        self.camera_selector.blockSignals(True) 
        self.camera_selector.clear()
        self.camera_selector.addItem("--- Chọn Camera ---", None)

        index_to_restore = 0 
        
        for cam_idx in cameras:
            self.camera_selector.addItem(f"Camera {cam_idx}", cam_idx)
            if current_cam_idx == cam_idx:
                index_to_restore = self.camera_selector.count() - 1

        self.camera_selector.setCurrentIndex(index_to_restore)
        self.camera_selector.blockSignals(False)
        
        self.camera_selector.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        
        if index_to_restore == 0 and current_cam_idx is not None:
             self.reset_ui_state()
             self.image_label.setText(f"Camera {current_cam_idx} đã bị ngắt kết nối.")

    def on_user_select_camera(self, index):
        cam_idx = self.camera_selector.currentData()
        self.reset_ui_state()
        
        if cam_idx is not None:
            self.btn_pause.setEnabled(True)
        
        self.camera_manager.change_camera(cam_idx)
        
        if cam_idx is None:
            self.image_label.setText("Đã dừng Camera.")
            self.image_label.setPixmap(QPixmap())

    def reset_ui_state(self):
        self.btn_pause.setChecked(False)
        self.btn_pause.setText("Tạm dừng")
        self.btn_pause.setEnabled(False)
        self.image_label.setStyleSheet("border: 2px solid #555; background-color: #222; color: #AAA;")
        self.image_label.setPixmap(QPixmap())

    @pyqtSlot(QImage)
    def update_image(self, qt_img):
        self.image_label.setPixmap(QPixmap.fromImage(qt_img))

    @pyqtSlot(str)
    def show_error(self, message):
        self.reset_ui_state()
        self.image_label.setText(f"LỖI: {message}\nĐang cập nhật lại danh sách...")
        self.image_label.setStyleSheet("border: 2px solid red; background-color: #300; color: #FFF; font-weight: bold;")
        
        self.camera_selector.blockSignals(True)
        self.camera_selector.setCurrentIndex(0) 
        self.camera_selector.blockSignals(False)

    @pyqtSlot(str)
    def update_status_text(self, text):
        if self.camera_selector.currentData() is None:
            self.image_label.setText(text)

    def closeEvent(self, event):
        self.camera_manager.stop_all()
        event.accept()