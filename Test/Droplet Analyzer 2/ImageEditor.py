# App/Presentation/Views/Widgets/FileEditorWorkspace/ImageEditor.py
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFileDialog, QSizePolicy, QMessageBox,
                             QGroupBox, QComboBox, QDialog, QScrollArea, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSlot, QSize, QThread
from PyQt6.QtGui import QPixmap, QIcon, QPainter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class CalibrationResultDialog(QDialog):
    """Dialog để hiển thị kết quả calibration"""
    def __init__(self, analysis_result, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calibration Result - Droplet Analysis")
        self.setGeometry(100, 100, 1000, 600)
        self.analysis_result = analysis_result
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Tạo matplotlib figure để hiển thị
        from matplotlib.figure import Figure
        fig = Figure(figsize=(10, 5), dpi=100)
        
        # Vẽ ảnh phân tích
        ax1 = fig.add_subplot(121)
        if self.analysis_result.analysis_image is not None:
            import cv2
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(self.analysis_result.analysis_image, cv2.COLOR_BGR2RGB)
            ax1.imshow(image_rgb)
        ax1.set_title("Droplet Analysis", fontsize=12, fontweight='bold')
        ax1.axis('off')

        # Vẽ thông tin kết quả
        ax2 = fig.add_subplot(122)
        ax2.axis('off')

        info_text = "DROPLET ANALYSIS RESULTS\n" + "="*40 + "\n\n"
        
        if self.analysis_result.success:
            info_text += "Contact Angle Measurements:\n"
            info_text += "-"*40 + "\n"
            
            if self.analysis_result.contact_angle_avg is not None:
                info_text += f"  Average:  {self.analysis_result.contact_angle_avg:.2f}°\n"
            if self.analysis_result.contact_angle_left is not None:
                info_text += f"  Left:     {self.analysis_result.contact_angle_left:.2f}°\n"
            if self.analysis_result.contact_angle_right is not None:
                info_text += f"  Right:    {self.analysis_result.contact_angle_right:.2f}°\n"
            
            info_text += "\nDroplet Dimensions:\n"
            info_text += "-"*40 + "\n"
            
            if self.analysis_result.droplet_width is not None:
                info_text += f"  Width:    {self.analysis_result.droplet_width:.2f} px\n"
            if self.analysis_result.droplet_height is not None:
                info_text += f"  Height:   {self.analysis_result.droplet_height:.2f} px\n"
            if self.analysis_result.base_diameter is not None:
                info_text += f"  Base:     {self.analysis_result.base_diameter:.2f} px\n"
            
            if self.analysis_result.fitted_circle is not None:
                info_text += "\nCircle Fitting:\n"
                info_text += "-"*40 + "\n"
                circle = self.analysis_result.fitted_circle
                info_text += f"  Major Axis: {circle['major_axis']:.2f} px\n"
                info_text += f"  Minor Axis: {circle['minor_axis']:.2f} px\n"
                info_text += f"  Angle:      {circle['angle']:.2f}°\n"
            
            if self.analysis_result.volume is not None:
                info_text += f"\nVolume (est.):  {self.analysis_result.volume:.2f} units³\n"
        else:
            info_text += f"Error: {self.analysis_result.error_message}\n"

        ax2.text(0.05, 0.95, info_text, fontsize=9, verticalalignment='top',
                fontfamily='monospace', 
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

        fig.tight_layout()

        # Thêm canvas vào layout
        canvas = FigureCanvas(fig)
        canvas.setParent(self)
        layout.addWidget(canvas)

        # Buttons
        button_layout = QHBoxLayout()
        
        btn_save = QPushButton("Save Result Image")
        btn_save.clicked.connect(self.save_result_image)
        button_layout.addWidget(btn_save)
        
        btn_export = QPushButton("Export Data")
        btn_export.clicked.connect(self.export_data)
        button_layout.addWidget(btn_export)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)

    def save_result_image(self):
        """Lưu ảnh kết quả phân tích"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Analysis Image", "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;BMP Image (*.bmp)"
        )
        
        if file_path and self.analysis_result.analysis_image is not None:
            try:
                import cv2
                cv2.imwrite(file_path, self.analysis_result.analysis_image)
                QMessageBox.information(self, "Success", f"Image saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save image: {str(e)}")

    def export_data(self):
        """Xuất dữ liệu phân tích thành file text"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Analysis Data", "",
            "Text File (*.txt);;CSV File (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("DROPLET ANALYSIS DATA\n")
                    f.write("="*50 + "\n\n")
                    
                    if self.analysis_result.success:
                        f.write("Contact Angles (degrees):\n")
                        f.write("-"*50 + "\n")
                        if self.analysis_result.contact_angle_avg is not None:
                            f.write(f"Average: {self.analysis_result.contact_angle_avg:.4f}\n")
                        if self.analysis_result.contact_angle_left is not None:
                            f.write(f"Left: {self.analysis_result.contact_angle_left:.4f}\n")
                        if self.analysis_result.contact_angle_right is not None:
                            f.write(f"Right: {self.analysis_result.contact_angle_right:.4f}\n")
                        
                        f.write("\nDroplet Dimensions (pixels):\n")
                        f.write("-"*50 + "\n")
                        if self.analysis_result.droplet_width is not None:
                            f.write(f"Width: {self.analysis_result.droplet_width:.2f}\n")
                        if self.analysis_result.droplet_height is not None:
                            f.write(f"Height: {self.analysis_result.droplet_height:.2f}\n")
                        if self.analysis_result.base_diameter is not None:
                            f.write(f"Base Diameter: {self.analysis_result.base_diameter:.2f}\n")
                        if self.analysis_result.volume is not None:
                            f.write(f"Volume: {self.analysis_result.volume:.4f} units³\n")
                    else:
                        f.write(f"Error: {self.analysis_result.error_message}\n")
                
                QMessageBox.information(self, "Success", f"Data exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export data: {str(e)}")


class ImageEditor(QWidget):
    def __init__(self, view_model, parent=None):
        super().__init__(parent)
        self.view_model = view_model
        self.current_pixmap = None
        self.calibration_worker = None

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
        self.btn_calibration.setToolTip("Calibration - Droplet Analysis")
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
        self.cmb_aspect.addItems(["Original", "1:1", "3:3", "16:9", "21:9"])
        self.cmb_aspect.setCurrentIndex(0)
        self.cmb_aspect.setFixedSize(100, 28)
        self.cmb_aspect.setToolTip("Select or enter aspect ratio (e.g., 16:9 or 1.5)")
        tools_layout.addWidget(self.cmb_aspect)

        # Đẩy các thành phần về bên trái
        tools_layout.addStretch()

        # Thêm GroupBox vào layout chính của panel
        control_layout.addWidget(tools_group)
        
        # Progress bar cho calibration (ẩn lúc đầu)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(0)  # Indeterminate progress
        self.progress_bar.setTextVisible(True)
        control_layout.addWidget(self.progress_bar)
        
        # Thêm stretch vào control_layout để đẩy GroupBox lên trên cùng
        control_layout.addStretch()
        
        main_layout.addWidget(control_panel, stretch=0)

    def connect_view_model_signals(self):
        self.view_model.image_loaded.connect(self.on_image_loaded)
        # ĐÃ XÓA kết nối error_occurred để không hiện hộp thoại lỗi
        # self.view_model.error_occurred.connect(self.on_error)
        self.view_model.aspect_ratio_changed.connect(self.on_aspect_ratio_changed)
        
        # Calibration signals
        self.view_model.calibration_started.connect(self.on_calibration_started)
        self.view_model.calibration_progress.connect(self.on_calibration_progress)
        self.view_model.calibration_completed.connect(self.on_calibration_completed)
        self.view_model.calibration_error.connect(self.on_calibration_error)

    def connect_ui_signals(self):
        self.btn_open.clicked.connect(self.on_open_clicked)
        self.btn_capture.clicked.connect(self.on_capture_clicked)
        self.btn_calibration.clicked.connect(self.on_calibration_clicked)
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

    @pyqtSlot()
    def on_calibration_clicked(self):
        """Xử lý khi nhấn nút Calibration"""
        if self.current_pixmap is None or self.current_pixmap.isNull():
            QMessageBox.warning(self, "No Image", "Vui lòng load ảnh trước khi calibration.")
            return
        
        # Bắt đầu calibration
        self.view_model.start_calibration()

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

    @pyqtSlot()
    def on_calibration_started(self):
        """Khi calibration bắt đầu"""
        self.progress_bar.setVisible(True)
        self.btn_calibration.setEnabled(False)
        self.btn_open.setEnabled(False)
        self.btn_capture.setEnabled(False)

    @pyqtSlot(str)
    def on_calibration_progress(self, message):
        """Cập nhật progress message"""
        self.progress_bar.setFormat(message)

    @pyqtSlot(object)
    def on_calibration_completed(self, analysis_result):
        """Khi calibration hoàn thành"""
        self.progress_bar.setVisible(False)
        self.btn_calibration.setEnabled(True)
        self.btn_open.setEnabled(True)
        self.btn_capture.setEnabled(True)
        
        if analysis_result.success:
            # Hiển thị dialog kết quả
            dialog = CalibrationResultDialog(analysis_result, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Calibration Failed", 
                              f"Error: {analysis_result.error_message}")

    @pyqtSlot(str)
    def on_calibration_error(self, error_message):
        """Khi xảy ra lỗi trong calibration"""
        self.progress_bar.setVisible(False)
        self.btn_calibration.setEnabled(True)
        self.btn_open.setEnabled(True)
        self.btn_capture.setEnabled(True)
        QMessageBox.critical(self, "Calibration Error", error_message)

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