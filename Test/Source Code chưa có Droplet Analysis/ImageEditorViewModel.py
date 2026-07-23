# App/Presentation/ViewModels/FeatureViewModel/ImageEditorViewModel.py
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap

class ImageEditorViewModel(QObject):
    image_loaded = pyqtSignal(QPixmap)
    error_occurred = pyqtSignal(str)
    aspect_ratio_changed = pyqtSignal(object)  # tuple (width, height) or None

    def __init__(self, project_name=None, item_name=None):
        super().__init__()
        self.project_name = project_name
        self.item_name = item_name
        self.current_pixmap = None
        self.aspect_ratio = None  # None = original, otherwise tuple (w, h)

    def load_image(self, file_path):
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.error_occurred.emit(f"Cannot load image: {file_path}")
        else:
            self.current_pixmap = pixmap
            self.image_loaded.emit(pixmap)

    def save_image(self, file_path):
        """Lưu pixmap hiện tại xuống đường dẫn file_path."""
        if self.current_pixmap and not self.current_pixmap.isNull():
            try:
                success = self.current_pixmap.save(file_path)
                if not success:
                    self.error_occurred.emit(f"Failed to save image to {file_path}")
            except Exception as e:
                self.error_occurred.emit(f"Error saving image: {str(e)}")
        else:
            self.error_occurred.emit("No image loaded to save.")

    def set_aspect_ratio(self, ratio_text):
        """
        Thiết lập tỉ lệ khung hình từ chuỗi nhập vào.
        ratio_text có thể là "Original", "1:1", "4:3", "16:9", "21:9"
        hoặc một chuỗi dạng "w:h" hoặc số thập phân.
        """
        if ratio_text == "Original":
            self.aspect_ratio = None
        else:
            parsed = self._parse_aspect_ratio(ratio_text)
            if parsed is not None:
                self.aspect_ratio = parsed
            else:
                self.error_occurred.emit(f"Invalid aspect ratio format: {ratio_text}")
                return
        self.aspect_ratio_changed.emit(self.aspect_ratio)

    def _parse_aspect_ratio(self, text):
        """Parse chuỗi tỉ lệ, trả về tuple (w, h) hoặc None."""
        text = text.strip()
        # Dạng "w:h"
        if ':' in text:
            parts = text.split(':')
            if len(parts) == 2:
                try:
                    w = float(parts[0])
                    h = float(parts[1])
                    if w > 0 and h > 0:
                        return (w, h)
                except ValueError:
                    pass
        # Dạng số thập phân (vd: 1.333)
        else:
            try:
                val = float(text)
                if val > 0:
                    # Quy ước: tỉ lệ = width/height, trả về (val, 1)
                    return (val, 1.0)
            except ValueError:
                pass
        return None