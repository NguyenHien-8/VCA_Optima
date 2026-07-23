# App/Presentation/ViewModels/FeatureViewModel/DropletAnalysisViewModel.py
from PyQt6.QtCore import QObject, pyqtSignal, QBuffer, QIODevice
from PyQt6.QtGui import QPixmap
import numpy as np
from PIL import Image
import io


class DropletAnalysisViewModel(QObject):
    analysis_completed = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    image_loaded = pyqtSignal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pixmap = None
        self.image_array = None
        self.analysis_data = None

    def load_image_from_pixmap(self, pixmap):
        """
        Load an image from QPixmap and convert it to a numpy array.
        Use QBuffer and PIL to avoid byteCount errors.
        """
        if pixmap is None or pixmap.isNull():
            self.error_occurred.emit("Invalid image provided")
            return False
        
        try:
            # Save pixmap to buffer as PNG
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.ReadWrite)
            pixmap.save(buffer, "PNG")
            buffer.seek(0)
            data = buffer.data().data()  # get bytes data

            # Use PIL to read image from bytes
            pil_image = Image.open(io.BytesIO(data))
            # Convert to grayscale (mode 'L') for analysis
            grayscale = pil_image.convert('L')
            self.image_array = np.array(grayscale)

            self.current_pixmap = pixmap
            self.image_loaded.emit(pixmap)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error loading image: {str(e)}")
            return False

    def perform_analysis(self):
        """
        Perform droplet analysis from the image array.
        Return the necessary data for drawing a heatmap.
        """
        if self.image_array is None:
            self.error_occurred.emit("No image data to analyze")
            return False
        
        try:
            # Normalize data to range [0, 255]
            img_min = np.min(self.image_array)
            img_max = np.max(self.image_array)
            
            if img_max > img_min:
                normalized = (self.image_array - img_min) / (img_max - img_min) * 255
            else:
                normalized = self.image_array
            
            # Compute statistics
            self.analysis_data = {
                'image': self.image_array,
                'normalized': normalized,
                'min_value': float(img_min),
                'max_value': float(img_max),
                'mean_value': float(np.mean(self.image_array)),
                'std_value': float(np.std(self.image_array)),
                'height': self.image_array.shape[0],
                'width': self.image_array.shape[1]
            }
            
            self.analysis_completed.emit(self.analysis_data)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error during analysis: {str(e)}")
            return False

    def get_analysis_data(self):
        """Get the current analysis data."""
        return self.analysis_data

    def get_heatmap_data(self):
        """Return data for drawing a heatmap (x, y, z)."""
        if self.analysis_data is None:
            return None
        
        img = self.analysis_data['normalized']
        height, width = img.shape
        
        # Create mesh grid for x, y
        x = np.linspace(0, 5.0, width)  # 5.0 mm width   
        y = np.linspace(3.0, 0.0, height)  # 3.0 mm height        
        X, Y = np.meshgrid(x, y)
        Z = img
        
        return X, Y, Z