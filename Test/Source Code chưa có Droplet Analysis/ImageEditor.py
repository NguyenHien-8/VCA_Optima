# App/Presentation/Views/Widgets/FileEditorWorkspace/ImageEditor.py
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFileDialog, QSizePolicy, QMessageBox,
                             QGroupBox, QComboBox)
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtGui import QPixmap, QIcon, QPainter

class ImageEditor(QWidget):
    def __init__(self, view_model, parent=None):
        super().__init__(parent)
        self.view_model = view_model
        self.current_pixmap = None

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("ImageEditor")

        self.setup_ui()
        self.connect_view_model_signals()
        self.connect_ui_signals()
        self.load_style()

    def load_style(self):
        # CẬP NHẬT: Trỏ tới file ImageEditorStyles.qss mới tạo
        qss_path = "App/ReSource/Styles/ImageEditorStyles.qss"
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def setup_ui(self):
        # Sử dụng QVBoxLayout: ảnh ở trên, control panel ở dưới
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Vùng hiển thị ảnh
        self.image_label = QLabel("No Image")
        self.image_label.setObjectName("ImageLabel")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setMinimumSize(200, 200)
        self.image_label.setScaledContents(True) 
        main_layout.addWidget(self.image_label, stretch=3)

        # Panel điều khiển nằm dưới
        control_panel = QWidget()
        control_panel.setObjectName("ControlPanel")
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(10)

        # --- GỘP CONTROL: Tạo một GroupBox chung cho Tools (Open, Capture, Aspect Ratio) ---
        tools_group = QGroupBox("Image Controls")
        tools_layout = QHBoxLayout(tools_group)
        tools_layout.setContentsMargins(10, 5, 10, 5)
        tools_layout.setSpacing(15) # Tăng khoảng cách giữa các phần tử cho thoáng

        # Đường dẫn icon cơ sở
        icon_base_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..",
            "ReSource", "Icon", "Media"
        )

        # 1. Nút Open Image
        self.btn_open = QPushButton()
        self.btn_open.setObjectName("MediaBtn")
        self.btn_open.setToolTip("Open Image")
        self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open.setFixedSize(50, 50)

        icon_open_path = os.path.join(icon_base_path, "image.svg")
        if os.path.exists(icon_open_path):
            self.btn_open.setIcon(QIcon(icon_open_path))
            self.btn_open.setIconSize(QSize(30, 30))

        tools_layout.addWidget(self.btn_open)

        # 2. Nút Capture Image
        self.btn_capture = QPushButton()
        self.btn_capture.setObjectName("MediaBtn")
        self.btn_capture.setToolTip("Capture Image")
        self.btn_capture.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_capture.setFixedSize(50, 50)
        
        icon_capture_path = os.path.join(icon_base_path, "photo_camera.svg")
        if os.path.exists(icon_capture_path):
            self.btn_capture.setIcon(QIcon(icon_capture_path))
            self.btn_capture.setIconSize(QSize(30, 30))
        
        tools_layout.addWidget(self.btn_capture)

        # 2.1 Nút Calibration (thêm mới)
        self.btn_calibration = QPushButton()
        self.btn_calibration.setObjectName("MediaBtn")          # giữ objectName để dùng chung style
        self.btn_calibration.setToolTip("Calibration")
        self.btn_calibration.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calibration.setFixedSize(50, 50)
        icon_calib_path = os.path.join(icon_base_path, "analysis.svg")
        if os.path.exists(icon_calib_path):
            self.btn_calibration.setIcon(QIcon(icon_calib_path))
            self.btn_calibration.setIconSize(QSize(30, 30))
        tools_layout.addWidget(self.btn_calibration)

        # Đường phân cách nhỏ giữa nhóm nút và nhóm Ratio
        line = QWidget()
        line.setFixedWidth(1)
        line.setFixedHeight(30)
        line.setStyleSheet("background-color: #555555;")
        tools_layout.addWidget(line)

        # 3. Aspect Ratio Control
        lbl_aspect = QLabel("Ratio:")
        lbl_aspect.setObjectName("SmallLabel")
        tools_layout.addWidget(lbl_aspect)

        self.cmb_aspect = QComboBox()
        self.cmb_aspect.setEditable(True)
        self.cmb_aspect.addItems(["Original", "1:1", "5:2", "21:9", "16:9"])
        self.cmb_aspect.setCurrentIndex(0)
        self.cmb_aspect.setFixedSize(100, 28)
        self.cmb_aspect.setToolTip("Select or enter aspect ratio (e.g., 16:9 or 1.5)")
        tools_layout.addWidget(self.cmb_aspect)

        # Đẩy các thành phần về bên trái
        tools_layout.addStretch()

        # Thêm GroupBox vào layout chính của panel
        control_layout.addWidget(tools_group)
        
        # Thêm stretch vào control_layout để đẩy GroupBox lên trên cùng
        control_layout.addStretch()
        
        main_layout.addWidget(control_panel, stretch=0)

    def connect_view_model_signals(self):
        self.view_model.image_loaded.connect(self.on_image_loaded)
        # ĐÃ XÓA kết nối error_occurred để không hiện hộp thoại lỗi
        # self.view_model.error_occurred.connect(self.on_error)
        self.view_model.aspect_ratio_changed.connect(self.on_aspect_ratio_changed)

    def connect_ui_signals(self):
        self.btn_open.clicked.connect(self.on_open_clicked)
        self.btn_capture.clicked.connect(self.on_capture_clicked)
        # (Chưa gán sự kiện cho btn_calibration – có thể bổ sung sau)
        self.cmb_aspect.currentTextChanged.connect(self.on_aspect_ratio_text_changed)

    @pyqtSlot()
    def on_open_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.view_model.load_image(file_path)

    @pyqtSlot()
    def on_capture_clicked(self):
        """Xử lý khi nhấn nút chụp: Hiện explorer hỏi lưu ở đâu, sau đó lưu ảnh hiện tại."""
        if self.current_pixmap is None or self.current_pixmap.isNull():
            QMessageBox.warning(self, "No Image", "Không có ảnh để chụp/lưu.")
            return

        # Hiển thị Explorer để người dùng chọn nơi lưu
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Captured Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            self.view_model.save_image(file_path)

    @pyqtSlot(str)
    def on_aspect_ratio_text_changed(self, text):
        """Khi người dùng chọn hoặc nhập tỉ lệ mới."""
        self.view_model.set_aspect_ratio(text)

    @pyqtSlot(object)
    def on_aspect_ratio_changed(self, ratio):
        """Khi view_model thông báo tỉ lệ thay đổi, cập nhật hiển thị."""
        self.update_image_display()

    @pyqtSlot(QPixmap)
    def on_image_loaded(self, pixmap):
        self.current_pixmap = pixmap
        self.update_image_display()

    @pyqtSlot(str)
    def on_error(self, message):
        # Hàm này vẫn giữ nhưng không được kết nối, nếu cần có thể dùng sau
        pass

    def update_image_display(self):
        """Cập nhật hiển thị ảnh dựa trên tỉ lệ đã chọn."""
        if self.current_pixmap is None:
            return
        label_size = self.image_label.size()
        if label_size.isEmpty():
            return

        # Lấy tỉ lệ từ view_model
        ratio = self.view_model.aspect_ratio

        if ratio is None:
            # Original: scale giữ nguyên tỉ lệ (KeepAspectRatio)
            scaled = self.current_pixmap.scaled(
                label_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
        else:
            # Áp dụng tỉ lệ khung hình mong muốn
            w_ratio, h_ratio = ratio
            target_ratio = w_ratio / h_ratio

            # Tính kích thước hiển thị dựa trên tỉ lệ và kích thước label
            label_width = label_size.width()
            label_height = label_size.height()
            label_ratio = label_width / label_height if label_height > 0 else 1.0

            if label_ratio > target_ratio:
                # Label rộng hơn tỉ lệ mục tiêu => chiều cao quyết định
                display_height = label_height
                display_width = int(display_height * target_ratio)
            else:
                # Label cao hơn tỉ lệ mục tiêu => chiều rộng quyết định
                display_width = label_width
                display_height = int(display_width / target_ratio)

            # Tạo pixmap mới với kích thước label, nền đen
            result_pixmap = QPixmap(label_size)
            result_pixmap.fill(Qt.GlobalColor.black)

            # Scale ảnh gốc với KeepAspectRatio đến kích thước display
            scaled_original = self.current_pixmap.scaled(
                display_width, display_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # Vẽ ảnh đã scale lên giữa result_pixmap
            painter = QPainter(result_pixmap)
            x_offset = (label_width - scaled_original.width()) // 2
            y_offset = (label_height - scaled_original.height()) // 2
            painter.drawPixmap(x_offset, y_offset, scaled_original)
            painter.end()

            self.image_label.setPixmap(result_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_pixmap:
            self.update_image_display()

    def load_image_from_file(self, file_path):
        """Public method to load image, used by drag and drop."""
        self.view_model.load_image(file_path)