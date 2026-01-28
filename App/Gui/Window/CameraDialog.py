from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QPushButton, 
                             QMessageBox, QFrame, QSizePolicy, QStyle)
from PyQt6.QtCore import Qt, pyqtSlot, QSize, QRect
from PyQt6.QtGui import QImage, QPixmap, QFont, QPainter, QPainterPath, QBrush, QColor

class CameraDialog(QDialog):
    def __init__(self, camera_manager, main_window):
        super().__init__(main_window)
        self.setWindowTitle("Camera Configuration")
        # Kích thước cố định toàn bộ Dialog
        self.setFixedSize(500, 280) 
        
        self.camera_manager = camera_manager
        self.main_window = main_window 
        
        self.first_load = True

        # 1. Lưu ID cũ để phòng trường hợp Cancel
        self.original_camera_id = self.camera_manager.active_camera_index
        self.selected_camera_id = self.original_camera_id
        
        # [FIX QUAN TRỌNG] Reset trạng thái "đang chạy" trong Manager về None.
        # Lý do: Khi nhấn Apply lần trước, ta đã lưu ID vào active_camera_index nhưng lại Stop thread.
        # Điều này khiến Manager lầm tưởng Camera vẫn đang chạy -> Từ chối lệnh Connect tiếp theo.
        # Việc set về None ở đây ép Manager phải khởi tạo lại luồng mới khi bấm Connect.
        self.camera_manager.active_camera_index = None

        self.setup_ui()
        self.handle_signals_on_open()
        
        # Quét camera
        self.camera_manager.scan_cameras()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        # ================= PHẦN TRÊN =================
        top_container = QHBoxLayout()
        
        # --- CỘT TRÁI ---
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        # Title
        lbl_title = QLabel("Camera:")
        font_title = QFont()
        font_title.setPointSize(14)
        lbl_title.setFont(font_title)
        left_layout.addWidget(lbl_title)

        # Combo box + Refresh button
        combo_row = QHBoxLayout()
        
        self.combo_cameras = QComboBox()
        self.combo_cameras.setPlaceholderText("Scanning devices...")
        self.combo_cameras.setFixedHeight(30)
        self.combo_cameras.currentIndexChanged.connect(self.on_combo_changed)
        combo_row.addWidget(self.combo_cameras)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedSize(30, 30)
        self.btn_refresh.setToolTip("Refresh Camera List")
        icon_refresh = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        self.btn_refresh.setIcon(icon_refresh)
        self.btn_refresh.clicked.connect(self.on_click_refresh)
        combo_row.addWidget(self.btn_refresh)
        
        left_layout.addLayout(combo_row)
        left_layout.addStretch()

        # Button Connect
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_connect.setFixedHeight(35)
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 4px; font-size: 13px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        self.btn_connect.clicked.connect(self.on_click_connect_preview)
        left_layout.addWidget(self.btn_connect)
        
        top_container.addLayout(left_layout, stretch=4) 

        # --- CỘT PHẢI: PREVIEW ---
        preview_container = QVBoxLayout()
        preview_container.setAlignment(Qt.AlignmentFlag.AlignCenter) 

        self.lbl_preview = QLabel("Camera Thread")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Kích thước CỐ ĐỊNH cho khung preview để không bị trượt/nhảy
        self.lbl_preview.setFixedSize(260, 195) 
        
        self.lbl_preview.setStyleSheet("""
            QLabel {
                background-color: #EEEEEE; 
                color: #333; 
                border: 2px solid #AAAAAA; 
                border-radius: 15px; 
                font-style: italic;
                font-size: 16px;
            }
        """)
        self.lbl_preview.setScaledContents(False)

        preview_container.addWidget(self.lbl_preview)
        top_container.addLayout(preview_container, stretch=6)
        
        main_layout.addLayout(top_container, stretch=1)

        # ================= PHẦN DƯỚI =================
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.btn_apply = QPushButton("Apply and Close")
        self.btn_apply.setFixedWidth(120)
        self.btn_apply.setFixedHeight(30)
        self.btn_apply.clicked.connect(self.on_click_apply)
        action_layout.addWidget(self.btn_apply)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedWidth(80)
        self.btn_cancel.setFixedHeight(30)
        self.btn_cancel.clicked.connect(self.on_click_cancel)
        action_layout.addWidget(self.btn_cancel)

        main_layout.addLayout(action_layout)

    # ================= LOGIC XỬ LÝ =================

    def handle_signals_on_open(self):
        """Chuyển signal từ MainWindow sang Dialog"""
        try:
            self.camera_manager.frame_received_signal.disconnect(self.main_window.update_image)
        except TypeError:
            pass 
        
        self.camera_manager.frame_received_signal.connect(self.update_preview_slot)
        self.camera_manager.camera_list_signal.connect(self.update_combo_box)

    def on_combo_changed(self, index):
        """Cập nhật ID khi người dùng chọn thủ công"""
        if index >= 0:
            self.selected_camera_id = self.combo_cameras.currentData()
        else:
            self.selected_camera_id = None

    def on_click_refresh(self):
        """Nút Refresh"""
        self.combo_cameras.setPlaceholderText("Scanning...")
        self.camera_manager.scan_cameras()

    def on_click_connect_preview(self):
        """Kích hoạt Camera xem trước"""
        if self.selected_camera_id is None:
             self.selected_camera_id = self.combo_cameras.currentData()

        cam_idx = self.selected_camera_id
        if cam_idx is None:
            QMessageBox.warning(self, "Warning", "Please select a camera device first!")
            return
        
        self.lbl_preview.setText("Connecting...")
        self.lbl_preview.setStyleSheet("background-color: #000; border: 2px solid #555; border-radius: 15px;")
        
        # [Safety Check] Đảm bảo active_index không chặn kết nối
        if self.camera_manager.active_camera_index == cam_idx:
            self.camera_manager.active_camera_index = None

        self.camera_manager.change_camera(cam_idx)

    @pyqtSlot(list)
    def update_combo_box(self, cam_indices):
        """Được gọi khi scan xong."""
        # Block signals để tránh hàm clear() kích hoạt on_combo_changed làm mất ID
        self.combo_cameras.blockSignals(True)
        self.combo_cameras.clear()
        self.combo_cameras.setPlaceholderText("Select device...")

        if not cam_indices:
            self.combo_cameras.addItem("No camera found", None)
            self.camera_manager.stop_current_camera()
            self.lbl_preview.clear()
            self.lbl_preview.setText("No Signal")
            self.lbl_preview.setStyleSheet("background-color: #EEE; color: #333; border: 2px solid #AAA; border-radius: 15px; font-style: italic; font-size: 16px;")
            self.combo_cameras.blockSignals(False)
            return
            
        for idx in cam_indices:
            self.combo_cameras.addItem(f"USB Camera (Index {idx})", idx)
        
        # Khôi phục lựa chọn từ self.original_camera_id hoặc self.selected_camera_id
        target_id = self.selected_camera_id if self.selected_camera_id is not None else self.original_camera_id
        idx_in_combo = self.combo_cameras.findData(target_id)
        
        if idx_in_combo >= 0:
            self.combo_cameras.setCurrentIndex(idx_in_combo)
            self.selected_camera_id = target_id 

            # Nếu là lần load đầu, tự động Connect
            if self.first_load:
                self.on_click_connect_preview()
                self.first_load = False
        else:
            self.selected_camera_id = None
            if self.combo_cameras.count() > 0:
                 self.combo_cameras.setCurrentIndex(0) 
                 self.selected_camera_id = self.combo_cameras.currentData()

            self.camera_manager.stop_current_camera()
            self.lbl_preview.clear()
            self.lbl_preview.setText("Device Disconnected")
            self.lbl_preview.setStyleSheet("background-color: #FFCDD2; color: #D32F2F; border: 2px solid #E57373; border-radius: 15px; font-style: italic; font-size: 14px;")

        self.combo_cameras.blockSignals(False)

    @pyqtSlot(QImage)
    def update_preview_slot(self, qt_img):
        """Hiển thị ảnh và BO TRÒN"""
        if qt_img.isNull(): return

        target_size = self.lbl_preview.size()
        pixmap = QPixmap.fromImage(qt_img)
        
        # Scale ảnh vừa khít khung (IgnoreAspectRatio)
        scaled_pixmap = pixmap.scaled(target_size, 
                                      Qt.AspectRatioMode.IgnoreAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)

        rounded = QPixmap(target_size)
        rounded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, target_size.width(), target_size.height(), 15, 15)

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled_pixmap)
        painter.end()

        self.lbl_preview.setPixmap(rounded)

    def on_click_apply(self):
        """Lưu cấu hình và đóng"""
        self.camera_manager.stop_current_camera()
        
        try:
            self.camera_manager.frame_received_signal.disconnect(self.update_preview_slot)
        except: pass
        
        # Lưu ID vừa chọn vào Manager để dùng cho Main Window
        self.camera_manager.active_camera_index = self.selected_camera_id
        self.accept()

    def on_click_cancel(self):
        """Hủy bỏ: trả về trạng thái cũ"""
        self.camera_manager.stop_current_camera()
        
        # Khôi phục lại ID ban đầu
        self.camera_manager.active_camera_index = self.original_camera_id

        try:
            self.camera_manager.frame_received_signal.disconnect(self.update_preview_slot)
        except: pass

        self.camera_manager.frame_received_signal.connect(self.main_window.update_image)
        self.reject()

    def closeEvent(self, event):
        self.on_click_cancel()