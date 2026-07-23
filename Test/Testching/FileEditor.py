import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QFrame, QMessageBox, 
                             QSizePolicy, QGridLayout, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtGui import QImage, QPixmap, QIcon

from App.ReSource.Styles.FileEditorStyles import FILE_EDITOR_STYLES

class FileEditor(QWidget):
    def __init__(self, view_model, parent=None):
        super().__init__(parent)
        self.view_model = view_model
        self.current_frame = None
        
        # Khởi tạo đường dẫn icon
        self._init_icon_paths()
        
        self.setup_ui()
        self.connect_signals()

    def _init_icon_paths(self):
        """Khởi tạo đường dẫn đến các icon"""
        # Tìm App root folder
        # FileEditor.py ở: App/Presentation/Views/Widgets/FileEditor.py
        # Cần đi lên 4 level để tới App folder
        try:
            current_file = os.path.abspath(__file__)
            # Đi lên 4 level: Widgets → Views → Presentation → App
            app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        except Exception:
            # Fallback nếu không tìm được
            app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        icon_base = os.path.join(app_root, "ReSource", "Icon", "Media")
        
        self.icon_photo_camera = os.path.join(icon_base, "photo_camera.ico")
        self.icon_video_camera = os.path.join(icon_base, "video_camera.ico")
        self.icon_pause_video = os.path.join(icon_base, "pause_video.ico")
        self.icon_play_video = os.path.join(icon_base, "play_video.ico")
        self.icon_stop_video = os.path.join(icon_base, "stop_video.ico")

    def _load_icon(self, icon_path, fallback_text=""):
        """Tải icon từ đường dẫn, nếu không có thì trả về rỗng"""
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            print(f"Warning: Icon not found at {icon_path}")
            return QIcon()

    def setup_ui(self):
        # --- MAIN LAYOUT (Horizontal: Left=Camera, Right=Controls) ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # ============================================================
        # 1. LEFT SIDE: CAMERA PREVIEWER
        # ============================================================
        self.preview_container = QWidget()
        self.preview_container.setStyleSheet("background-color: #000000;")
        preview_layout = QVBoxLayout(self.preview_container)
        preview_layout.setContentsMargins(0,0,0,0)

        self.lbl_camera = QLabel("Camera Offline")
        self.lbl_camera.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_camera.setStyleSheet("color: #666666; font-size: 16px;")
        self.lbl_camera.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.lbl_camera.setMinimumSize(20, 240)
        self.lbl_camera.setScaledContents(True) 
        
        preview_layout.addWidget(self.lbl_camera)
        main_layout.addWidget(self.preview_container, stretch=3)

        # ============================================================
        # 2. RIGHT SIDE: CONTROL PANEL (Motor + Media)
        # ============================================================
        self.control_panel = QWidget()
        self.control_panel.setStyleSheet(FILE_EDITOR_STYLES) 
        
        control_layout = QVBoxLayout(self.control_panel)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(10)

        # --- A. MOTOR CONTROLS ---
        motor_group = QGroupBox("Motor Control")
        motor_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        motor_inner_layout = QHBoxLayout(motor_group)
        motor_inner_layout.setContentsMargins(1, 1, 1, 1)
        motor_inner_layout.setSpacing(5)
        motor_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 

        # -------------------------------------------------------
        # LEFT COLUMN: Input Height & Speed
        # -------------------------------------------------------
        input_grid = QGridLayout()
        input_grid.setVerticalSpacing(50)   # Vertical distance between lines Height and Speed
        input_grid.setHorizontalSpacing(10) # # Horizontal distance between Label - Box - Unit

        # -- Row Height (Row 0) --
        lbl_h = QLabel("Height:")
        lbl_h.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)   
        self.cmb_height = QComboBox()
        self.cmb_height.setEditable(True)
        self.cmb_height.addItems(["2", "5", "10", "20", "50"])
        self.cmb_height.setFixedSize(120, 28)    
        lbl_unit_h = QLabel("mm")
        lbl_unit_h.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        input_grid.addWidget(lbl_h, 0, 0)
        input_grid.addWidget(self.cmb_height, 0, 1)
        input_grid.addWidget(lbl_unit_h, 0, 2)

        # -- Row Speed (Row 1) --
        lbl_s = QLabel("Speed:")
        lbl_s.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)  
        self.cmb_speed = QComboBox()
        self.cmb_speed.setEditable(True)
        self.cmb_speed.addItems(["Slow", "Medium", "Fast"])
        self.cmb_speed.setFixedSize(120, 28)
        lbl_unit_s = QLabel("rpm")
        lbl_unit_s.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        input_grid.addWidget(lbl_s, 1, 0)
        input_grid.addWidget(self.cmb_speed, 1, 1)
        input_grid.addWidget(lbl_unit_s, 1, 2)
        
        # Sử dụng Wrapper Widget căn giữa input_grid theo chiều dọc (AlignVCenter)
        input_container = QWidget()
        input_container.setLayout(input_grid)
        motor_inner_layout.addWidget(input_container, stretch=0, alignment=Qt.AlignmentFlag.AlignVCenter)

        # -------------------------------------------------------
        # RIGHT COLUMN: Navigation buttons (Up/Down/Stop)
        # ------------------------------------------------------- 
        ctrl_layout = QVBoxLayout()
        ctrl_layout.setSpacing(8)
        ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_up = QPushButton("▲")
        self.btn_up.setObjectName("DirectionBtn") 
        self.btn_up.setFixedSize(50, 50)
        self.btn_up.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_up.setToolTip("Move Up")

        self.btn_stop = QPushButton("⊘")
        self.btn_stop.setObjectName("StopBtn")
        self.btn_stop.setFixedSize(50, 50)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.setToolTip("Stop Motor")

        self.btn_down = QPushButton("▼")
        self.btn_down.setObjectName("DirectionBtn") 
        self.btn_down.setFixedSize(50, 50)
        self.btn_down.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_down.setToolTip("Move Down")

        ctrl_layout.addWidget(self.btn_up)
        ctrl_layout.addWidget(self.btn_stop)
        ctrl_layout.addWidget(self.btn_down)
        
        # Wrapper Widget cho cột buttons
        ctrl_container = QWidget()
        ctrl_container.setLayout(ctrl_layout)
        motor_inner_layout.addWidget(ctrl_container, stretch=0, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        control_layout.addWidget(motor_group)

        # --- B. MEDIA CONTROLS (Capture/Record) ---
        media_group = QGroupBox("Camera & Video")
        # Giữ nguyên: Khóa chiều cao Media Group
        media_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        media_layout = QVBoxLayout(media_group)
        media_layout.setSpacing(10)
        
        # ========== NÚT CAPTURE IMAGE (với icon) ==========
        self.btn_capture = QPushButton()
        self.btn_capture.setObjectName("MediaBtn")
        self.btn_capture.setIcon(self._load_icon(self.icon_photo_camera))
        self.btn_capture.setIconSize(QSize(40, 40))
        self.btn_capture.setFixedSize(60, 60)
        self.btn_capture.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_capture.setToolTip("Capture Image (Photo)")
        media_layout.addWidget(self.btn_capture, alignment=Qt.AlignmentFlag.AlignCenter)

        # Grid cho các nút Video
        video_grid = QGridLayout()
        video_grid.setHorizontalSpacing(15)
        video_grid.setVerticalSpacing(15)
        
        # ========== NÚT RECORD VIDEO (với icon) ==========
        self.btn_record = QPushButton()
        self.btn_record.setObjectName("MediaBtn")
        self.btn_record.setIcon(self._load_icon(self.icon_video_camera))
        self.btn_record.setIconSize(QSize(40, 40))
        self.btn_record.setFixedSize(60, 60)
        self.btn_record.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_record.setToolTip("Record Video")
        
        # ========== NÚT PAUSE VIDEO (với icon) ==========
        self.btn_pause = QPushButton()
        self.btn_pause.setObjectName("MediaBtn")
        self.btn_pause.setIcon(self._load_icon(self.icon_pause_video))
        self.btn_pause.setIconSize(QSize(40, 40))
        self.btn_pause.setFixedSize(60, 60)
        self.btn_pause.setVisible(False)
        self.btn_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pause.setToolTip("Pause Video")
        
        # ========== NÚT RESUME/PLAY VIDEO (với icon) ==========
        self.btn_resume = QPushButton()
        self.btn_resume.setObjectName("MediaBtn")
        self.btn_resume.setIcon(self._load_icon(self.icon_play_video))
        self.btn_resume.setIconSize(QSize(40, 40))
        self.btn_resume.setFixedSize(60, 60)
        self.btn_resume.setVisible(False)
        self.btn_resume.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_resume.setToolTip("Resume Video")
        
        # ========== NÚT STOP VIDEO (với icon) ==========
        self.btn_stop_video = QPushButton()
        self.btn_stop_video.setObjectName("MediaBtn")
        self.btn_stop_video.setIcon(self._load_icon(self.icon_stop_video))
        self.btn_stop_video.setIconSize(QSize(40, 40))
        self.btn_stop_video.setFixedSize(60, 60)
        self.btn_stop_video.setVisible(False)
        self.btn_stop_video.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop_video.setToolTip("Stop Video")

        # Sắp xếp nút video trong grid
        # Row 0: Record Video (nằm giữa)
        video_grid.addWidget(self.btn_record, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Row 1: Pause Video và Stop Video
        video_grid.addWidget(self.btn_pause, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        video_grid.addWidget(self.btn_stop_video, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Row 1, Col 0: Resume Video (thay thế Pause khi pause)
        video_grid.addWidget(self.btn_resume, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        media_layout.addLayout(video_grid)
        control_layout.addWidget(media_group)

        # Spacer bottom để đẩy mọi thứ lên trên
        control_layout.addStretch()

        # Thêm Panel phải vào Main Layout (stretch=1)
        main_layout.addWidget(self.control_panel, stretch=1)

    def connect_signals(self):
        # Kết nối ViewModel signals
        self.view_model.frame_received.connect(self.update_image)
        self.view_model.video_state_changed.connect(self.update_video_ui)
        self.view_model.error_occurred.connect(self.show_error)

        # Kết nối UI events - MOTOR
        self.btn_up.clicked.connect(self.on_up)
        self.btn_down.clicked.connect(self.on_down)
        self.btn_stop.clicked.connect(self.on_stop)

        # Kết nối UI events - MEDIA
        self.btn_capture.clicked.connect(self.on_capture)
        self.btn_record.clicked.connect(self.on_record)
        self.btn_pause.clicked.connect(self.on_pause)
        self.btn_resume.clicked.connect(self.on_resume)
        self.btn_stop_video.clicked.connect(self.on_stop_video)

    # Thêm resizeEvent để cập nhật ảnh khi widget thay đổi kích thước
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_frame and not self.current_frame.isNull():
            self.update_image(self.current_frame)

    @pyqtSlot(QImage)
    def update_image(self, q_img):
        """Nhận ảnh từ ViewModel và hiển thị"""
        self.current_frame = q_img  # Lưu lại để chụp
        # Kiểm tra kích thước label để tránh scale với size 0
        if self.lbl_camera.size().isEmpty():
            return
        pixmap = QPixmap.fromImage(q_img)
        
        scaled_pixmap = pixmap.scaled(self.lbl_camera.size(), 
                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
        self.lbl_camera.setPixmap(scaled_pixmap)

    @pyqtSlot(str)
    def update_video_ui(self, state):
        """Cập nhật trạng thái nút bấm Video"""
        if state == 'idle':
            self.btn_record.setVisible(True)
            self.btn_pause.setVisible(False)
            self.btn_resume.setVisible(False)
            self.btn_stop_video.setVisible(False)
            self.btn_capture.setEnabled(True)
        elif state == 'recording':
            self.btn_record.setVisible(False)
            self.btn_pause.setVisible(True)
            self.btn_stop_video.setVisible(True)
            self.btn_resume.setVisible(False)
            self.btn_capture.setEnabled(False) 
        elif state == 'paused':
            self.btn_record.setVisible(False)
            self.btn_pause.setVisible(False)
            self.btn_stop_video.setVisible(True)
            self.btn_resume.setVisible(True)

    @pyqtSlot(str)
    def show_error(self, msg):
        QMessageBox.warning(self, "Thông báo", msg)

    # --- Motor slots ---
    def on_up(self):
        h = self.cmb_height.currentText()
        s = self.cmb_speed.currentText()
        self.view_model.move_up(h, s)

    def on_down(self):
        h = self.cmb_height.currentText()
        s = self.cmb_speed.currentText()
        self.view_model.move_down(h, s)

    def on_stop(self):
        self.view_model.stop_motor()

    # --- Camera/Video slots ---
    def on_capture(self):
        if self.current_frame:
            self.view_model.capture_image(self.current_frame)
        else:
            self.show_error("Chưa có ảnh từ camera")

    def on_record(self):
        self.view_model.start_video()

    def on_pause(self):
        self.view_model.pause_video()

    def on_resume(self):
        self.view_model.resume_video()

    def on_stop_video(self):
        self.view_model.stop_video()