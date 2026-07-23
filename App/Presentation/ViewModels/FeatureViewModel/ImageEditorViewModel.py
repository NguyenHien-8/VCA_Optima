# App/Presentation/ViewModels/FeatureViewModel/ImageEditorViewModel.py
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap

class ImageEditorViewModel(QObject):
    image_loaded = pyqtSignal(QPixmap)
    error_occurred = pyqtSignal(str)

    def __init__(self, project_name=None, item_name=None):
        super().__init__()
        self.project_name = project_name
        self.item_name = item_name
        self.current_pixmap = None

    def load_image(self, file_path):
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.error_occurred.emit(f"Cannot load image: {file_path}")
        else:
            self.current_pixmap = pixmap
            self.image_loaded.emit(pixmap)

    def save_image(self, file_path):
        """Save the current pixmap to the given file path."""
        if self.current_pixmap and not self.current_pixmap.isNull():
            try:
                success = self.current_pixmap.save(file_path)
                if not success:
                    self.error_occurred.emit(f"Failed to save image to {file_path}")
            except Exception as e:
                self.error_occurred.emit(f"Error saving image: {str(e)}")
        else:
            self.error_occurred.emit("No image loaded to save.")