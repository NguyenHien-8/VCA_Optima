# App/Presentation/ViewModels/FeatureViewModel/ImageEditorViewModel.py
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap
import cv2
import numpy as np
from matplotlib.figure import Figure
import os

class ImageEditorViewModel(QObject):
    image_loaded = pyqtSignal(QPixmap)
    error_occurred = pyqtSignal(str)
    aspect_ratio_changed = pyqtSignal(object)  # tuple (width, height) or None
    
    # Calibration signals
    calibration_started = pyqtSignal()
    calibration_progress = pyqtSignal(str)
    calibration_completed = pyqtSignal(object)
    calibration_error = pyqtSignal(str)

    def __init__(self, project_name=None, item_name=None):
        super().__init__()
        self.project_name = project_name
        self.item_name = item_name
        self.current_pixmap = None
        self.aspect_ratio = None
        self._analyzer = None

    @property
    def analyzer(self):
        """Lazy initialization của DropletAnalyzer"""
        if self._analyzer is None:
            from App.Models.Analysis.DropletAnalyzer import DropletAnalyzer
            self._analyzer = DropletAnalyzer()
            # Connect signals
            self._analyzer.analysis_completed.connect(self.calibration_completed)
            self._analyzer.analysis_error.connect(self.calibration_error)
            self._analyzer.progress_updated.connect(self.calibration_progress)
        return self._analyzer

    def load_image(self, file_path):
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.error_occurred.emit(f"Cannot load image: {file_path}")
        else:
            self.current_pixmap = pixmap
            self.image_loaded.emit(pixmap)

    def save_image(self, file_path):
        """Save the current pixmap to the file_path."""
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
        Set the aspect ratio from the input string.
        ratio_text can be "Original", "1:1", "4:3", "16:9", "21:9"
        or a string like "w:h" or a decimal number.
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
        """Parse the scaled string, returning either tuple(w, h) or None."""
        text = text.strip()
        # Form "w:h"
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
        else:
            try:
                val = float(text)
                if val > 0:
                    # Convention: ratio = width/height, return (val, 1)
                    return (val, 1.0)
            except ValueError:
                pass
        return None

    def start_calibration(self):
        """
        Start the droplet calibration process.
        Use current_pixmap for analysis.
        """
        if self.current_pixmap is None or self.current_pixmap.isNull():
            self.calibration_error.emit("No image loaded for calibration")
            return
        
        self.calibration_started.emit()
        # Call the analyzer to perform the analysis.
        self.analyzer.analyze_from_pixmap(
            self.current_pixmap, 
            aspect_ratio=self.aspect_ratio
        )

    def visualize_result(self, analysis_result, output_path=None):
        """
        Visualize kết quả phân tích bằng matplotlib.
        
        Args:
            analysis_result: DropletAnalysisResult object
            output_path: Đường dẫn lưu ảnh (nếu None thì chỉ tạo figure)
        
        Returns:
            matplotlib Figure object
        """
        fig = Figure(figsize=(12, 5))
        
        # Vẽ ảnh phân tích
        ax1 = fig.add_subplot(121)
        if analysis_result.analysis_image is not None:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(analysis_result.analysis_image, cv2.COLOR_BGR2RGB)
            ax1.imshow(image_rgb)
        ax1.set_title("Droplet Analysis Result")
        ax1.axis('off')
        
        # Vẽ thông tin
        ax2 = fig.add_subplot(122)
        ax2.axis('off')
        
        # Sử dụng phương thức get_formatted_results từ analysis_result
        if analysis_result.success:
            info_text = "Analysis Results:\n" + "="*30 + "\n"
            info_text += analysis_result.get_formatted_results()
        else:
            info_text = f"Error: {analysis_result.error_message}\n"
        
        ax2.text(0.1, 0.5, info_text, fontsize=10, verticalalignment='center',
                fontfamily='monospace', bbox=dict(boxstyle='round', 
                facecolor='wheat', alpha=0.5))
        
        fig.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=100, bbox_inches='tight')
            print(f"Analysis result saved to: {output_path}")
        
        return fig

    def visualize_calibration_result(self, analysis_result, output_path=None):
        """
        Visualize calibration results using matplotlib.
        
        Args:
            analysis_result: DropletAnalysisResult object
            output_path: Visualization image save path
        
        Returns:
            matplotlib Figure object
        """
        try:
            fig = self.visualize_result(analysis_result, output_path)
            return fig
        except Exception as e:
            self.error_occurred.emit(f"Visualization error: {str(e)}")
            return None