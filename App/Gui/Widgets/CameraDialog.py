from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot

class CameraDialog(QDialog):
    def __init__(self, camera_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Camera Configuration")
        self.setMinimumWidth(350)
        self.camera_manager = camera_manager
        
        # UI Setup
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 1. Label trạng thái
        self.lbl_status = QLabel("Status: Waiting...")
        layout.addWidget(self.lbl_status)

        # 2. Chọn Camera
        hbox_cam = QHBoxLayout()
        hbox_cam.addWidget(QLabel("Camera:"))
        self.combo_cameras = QComboBox()
        hbox_cam.addWidget(self.combo_cameras)
        layout.addLayout(hbox_cam)

        # 3. Các nút chức năng
        hbox_btns = QHBoxLayout()
        
        self.btn_refresh = QPushButton("Refresh List")
        self.btn_refresh.clicked.connect(self.on_refresh)
        hbox_btns.addWidget(self.btn_refresh)

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.on_connect)
        hbox_btns.addWidget(self.btn_connect)

        layout.addLayout(hbox_btns)

        # 4. Nút Pause/Resume
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setCheckable(True)
        self.btn_pause.clicked.connect(self.on_pause)
        self.btn_pause.setEnabled(False) # Chỉ active khi đã kết nối
        layout.addWidget(self.btn_pause)

        # --- SIGNAL CONNECTIONS ---
        # Lắng nghe tín hiệu từ CameraManager để cập nhật UI dialog này
        self.camera_manager.camera_list_signal.connect(self.update_list_ui)
        self.camera_manager.error_occurred_signal.connect(self.show_error)
        
        # Khởi tạo dữ liệu ban đầu
        self.init_state()

    def init_state(self):
        """Khôi phục trạng thái UI dựa trên tình trạng hiện tại của CameraManager"""
        # Nếu đang có camera chạy
        if self.camera_manager.active_camera_index is not None:
            self.lbl_status.setText(f"Running Camera {self.camera_manager.active_camera_index}")
            self.btn_pause.setEnabled(True)
            self.btn_connect.setText("Change Camera")
        else:
            # Nếu chưa có camera, tự động quét list
            self.on_refresh()

    def on_refresh(self):
        self.lbl_status.setText("Scanning devices...")
        self.camera_manager.scan_cameras()

    def on_connect(self):
        idx = self.combo_cameras.currentData()
        if idx is not None:
            self.camera_manager.change_camera(idx)
            self.lbl_status.setText(f"Connected to Camera {idx}")
            self.btn_pause.setEnabled(True)
            self.btn_pause.setChecked(False)
            self.btn_pause.setText("Pause")
        else:
            QMessageBox.warning(self, "Warning", "Please select a Camera first!")

    def on_pause(self):
        is_paused = self.btn_pause.isChecked()
        self.camera_manager.set_paused(is_paused)
        if is_paused:
            self.btn_pause.setText("Resume")
            self.lbl_status.setText("Paused")
        else:
            self.btn_pause.setText("Pause")
            self.lbl_status.setText("Running")

    @pyqtSlot(list)
    def update_list_ui(self, cam_indices):
        self.combo_cameras.clear()
        if not cam_indices:
            self.lbl_status.setText("No Camera found!")
            return
            
        for idx in cam_indices:
            self.combo_cameras.addItem(f"Camera Port {idx}", idx)
        
        # Nếu đang chạy camera nào thì set combo box về đúng camera đó
        if self.camera_manager.active_camera_index is not None:
            index = self.combo_cameras.findData(self.camera_manager.active_camera_index)
            if index >= 0:
                self.combo_cameras.setCurrentIndex(index)
        
        self.lbl_status.setText("Updated camera list.")

    @pyqtSlot(str)
    def show_error(self, err_msg):
        self.lbl_status.setText(f"Error: {err_msg}")