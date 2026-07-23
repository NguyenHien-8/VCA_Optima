# App/Presentation/ViewModels/FeatureViewModel/ImageEditorViewModel.py
"""
ImageEditor ViewModel - Quản lý xử lý ảnh và phân tích giọt nước.

IMPROVEMENT NOTES:
- Thêm logging chi tiết để debug vấn đề import pyDSA_core
- Hiển thị rõ ràng thông báo nếu pyDSA_core không khả dụng
- Hỗ trợ fallback một cách mượt mà nếu không có pyDSA_core
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap
import cv2
import numpy as np
from matplotlib.figure import Figure
import os
import logging
import sys

# ==================== SETUP LOGGING ====================
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Tạo handler để in ra console
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# ==================== KIỂM TRA PYDSA_CORE ====================
def check_pydsa_availability():
    """
    Kiểm tra sự có mặt của pyDSA_core và trả về trạng thái chi tiết.
    
    Returns:
        dict: {
            'available': bool,
            'error': str or None,
            'missing_modules': list,
            'solution': str
        }
    """
    logger.info("=" * 60)
    logger.info("Checking pyDSA_core availability...")
    logger.info("=" * 60)
    
    required_modules = ['pyDSA_core', 'DropletProfile', 'BaselineDetector', 'ContactAngleCalculator']
    missing_modules = []
    
    # Kiểm tra từng module
    try:
        logger.info("Attempting to import 'pyDSA_core'...")
        from pyDSA_core import DropletProfile, BaselineDetector, ContactAngleCalculator
        
        logger.info("✓ SUCCESS: pyDSA_core imported successfully!")
        logger.info("  - DropletProfile: OK")
        logger.info("  - BaselineDetector: OK")
        logger.info("  - ContactAngleCalculator: OK")
        
        return {
            'available': True,
            'error': None,
            'missing_modules': [],
            'solution': None
        }
    
    except ImportError as e:
        error_str = str(e)
        logger.warning(f"✗ FAILED: Cannot import pyDSA_core")
        logger.warning(f"  Error: {error_str}")
        
        # Phân tích loại lỗi
        if "No module named 'pyDSA_core'" in error_str:
            missing_modules = ['pyDSA_core']
            solution = "pyDSA_core is not installed. Install it using: pip install pyDSA-core"
        elif "No module named" in error_str:
            # Lấy tên module bị thiếu
            import re
            match = re.search(r"No module named '([^']+)'", error_str)
            if match:
                missing_modules = [match.group(1)]
            solution = f"Missing dependency: {error_str}. Check your Python environment."
        else:
            solution = f"Import error: {error_str}. This might be a compatibility issue."
        
        logger.warning(f"  Missing modules: {missing_modules}")
        logger.warning(f"  Solution: {solution}")
        
        return {
            'available': False,
            'error': error_str,
            'missing_modules': missing_modules,
            'solution': solution
        }
    
    except Exception as e:
        logger.error(f"✗ UNEXPECTED ERROR: {str(e)}")
        return {
            'available': False,
            'error': str(e),
            'missing_modules': [],
            'solution': "Unexpected error occurred. Check logs for details."
        }


# Thực hiện kiểm tra
pydsa_check = check_pydsa_availability()
PYDSA_AVAILABLE = pydsa_check['available']

if PYDSA_AVAILABLE:
    logger.info("\n" + "=" * 60)
    logger.info("✓ Using pyDSA_core analyzer (RECOMMENDED)")
    logger.info("=" * 60 + "\n")
    from App.Models.Analysis.DropletAnalyzer_pyDSA import DropletAnalyzer_pyDSA as DropletAnalyzer
    ANALYZER_NAME = "pyDSA_core (Advanced)"
else:
    logger.warning("\n" + "=" * 60)
    logger.warning("✗ Using Algorithm Fallback (DEGRADED MODE)")
    logger.warning("-" * 60)
    logger.warning(f"Reason: {pydsa_check['error']}")
    logger.warning(f"Solution: {pydsa_check['solution']}")
    logger.warning("=" * 60 + "\n")
    from App.Models.Analysis.DropletAnalyzer_Algorithm import DropletAnalyzer_Algorithm as DropletAnalyzer
    ANALYZER_NAME = "Algorithm (Fallback)"


# ==================== MAIN VIEWMODEL CLASS ====================
class ImageEditorViewModel(QObject):
    """ViewModel quản lý image editing và calibration."""
    
    image_loaded = pyqtSignal(QPixmap)
    error_occurred = pyqtSignal(str)
    aspect_ratio_changed = pyqtSignal(object)  # tuple (width, height) or None
    
    # Calibration signals
    calibration_started = pyqtSignal()
    calibration_progress = pyqtSignal(str)
    calibration_completed = pyqtSignal(object)
    calibration_error = pyqtSignal(str)
    
    # New signal: Notify about analyzer availability
    analyzer_status_changed = pyqtSignal(str, bool)  # (analyzer_name, is_pydsa)

    def __init__(self, project_name=None, item_name=None):
        super().__init__()
        self.project_name = project_name
        self.item_name = item_name
        self.current_pixmap = None
        self.aspect_ratio = None
        self._analyzer = None
        
        # Log khởi tạo
        logger.info(f"\n[ImageEditorViewModel] Initialized with:")
        logger.info(f"  - Project: {project_name}")
        logger.info(f"  - Item: {item_name}")
        logger.info(f"  - Analyzer: {ANALYZER_NAME}")
        logger.info(f"  - pyDSA Available: {PYDSA_AVAILABLE}")
        
        # Phát signal thông báo trạng thái
        self.analyzer_status_changed.emit(ANALYZER_NAME, PYDSA_AVAILABLE)

    @property
    def analyzer(self):
        """Lazy initialization của DropletAnalyzer"""
        if self._analyzer is None:
            logger.info(f"[ImageEditorViewModel] Initializing {ANALYZER_NAME} analyzer...")
            
            try:
                self._analyzer = DropletAnalyzer()
                
                # Connect signals
                self._analyzer.analysis_completed.connect(self.calibration_completed)
                self._analyzer.analysis_error.connect(self.calibration_error)
                self._analyzer.progress_updated.connect(self.calibration_progress)
                
                logger.info(f"[ImageEditorViewModel] ✓ {ANALYZER_NAME} analyzer initialized successfully")
            except Exception as e:
                logger.error(f"[ImageEditorViewModel] ✗ Failed to initialize analyzer: {str(e)}")
                self.error_occurred.emit(f"Failed to initialize analyzer: {str(e)}")
                raise
        
        return self._analyzer

    def load_image(self, file_path):
        """Load image từ file path"""
        logger.info(f"[ImageEditorViewModel] Loading image: {file_path}")
        
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            error_msg = f"Cannot load image: {file_path}"
            logger.error(f"[ImageEditorViewModel] ✗ {error_msg}")
            self.error_occurred.emit(error_msg)
        else:
            self.current_pixmap = pixmap
            logger.info(f"[ImageEditorViewModel] ✓ Image loaded successfully ({pixmap.width()}x{pixmap.height()})")
            self.image_loaded.emit(pixmap)

    def save_image(self, file_path):
        """Save the current pixmap to the file_path."""
        logger.info(f"[ImageEditorViewModel] Saving image to: {file_path}")
        
        if self.current_pixmap and not self.current_pixmap.isNull():
            try:
                success = self.current_pixmap.save(file_path)
                if not success:
                    error_msg = f"Failed to save image to {file_path}"
                    logger.error(f"[ImageEditorViewModel] ✗ {error_msg}")
                    self.error_occurred.emit(error_msg)
                else:
                    logger.info(f"[ImageEditorViewModel] ✓ Image saved successfully")
            except Exception as e:
                error_msg = f"Error saving image: {str(e)}"
                logger.error(f"[ImageEditorViewModel] ✗ {error_msg}")
                self.error_occurred.emit(error_msg)
        else:
            error_msg = "No image loaded to save."
            logger.warning(f"[ImageEditorViewModel] {error_msg}")
            self.error_occurred.emit(error_msg)

    def set_aspect_ratio(self, ratio_text):
        """
        Set the aspect ratio from the input string.
        ratio_text can be "Original", "1:1", "4:3", "16:9", "21:9"
        or a string like "w:h" or a decimal number.
        """
        logger.info(f"[ImageEditorViewModel] Setting aspect ratio: {ratio_text}")
        
        if ratio_text == "Original":
            self.aspect_ratio = None
            logger.info(f"[ImageEditorViewModel] ✓ Aspect ratio set to Original")
        else:
            parsed = self._parse_aspect_ratio(ratio_text)
            if parsed is not None:
                self.aspect_ratio = parsed
                logger.info(f"[ImageEditorViewModel] ✓ Aspect ratio set to {parsed}")
            else:
                error_msg = f"Invalid aspect ratio format: {ratio_text}"
                logger.warning(f"[ImageEditorViewModel] {error_msg}")
                self.error_occurred.emit(error_msg)
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
        
        Improvements:
        - Sử dụng pyDSA_core nếu có sẵn
        - Fallback sang phương pháp cũ nếu cần
        - Better error handling với logging chi tiết
        """
        logger.info("\n" + "=" * 60)
        logger.info("[ImageEditorViewModel] Starting calibration...")
        logger.info(f"Using analyzer: {ANALYZER_NAME}")
        logger.info("=" * 60)
        
        if self.current_pixmap is None or self.current_pixmap.isNull():
            error_msg = "No image loaded for calibration"
            logger.error(f"[ImageEditorViewModel] ✗ {error_msg}")
            self.calibration_error.emit(error_msg)
            return
        
        self.calibration_started.emit()
        
        logger.info(f"[ImageEditorViewModel] Image size: {self.current_pixmap.width()}x{self.current_pixmap.height()}")
        logger.info(f"[ImageEditorViewModel] Aspect ratio: {self.aspect_ratio}")
        logger.info(f"[ImageEditorViewModel] Starting analysis...")
        
        # Call the analyzer to perform the analysis.
        self.analyzer.analyze_from_pixmap(
            self.current_pixmap, 
            aspect_ratio=self.aspect_ratio
        )

    def get_analyzer_status(self):
        """Get current analyzer status and solution if not available."""
        return {
            'name': ANALYZER_NAME,
            'available': PYDSA_AVAILABLE,
            'check_info': pydsa_check
        }

    def visualize_result(self, analysis_result, output_path=None):
        """
        Visualize kết quả phân tích bằng matplotlib.
        
        Args:
            analysis_result: DropletAnalysisResult object
            output_path: Đường dẫn lưu ảnh (nếu None thì chỉ tạo figure)
        
        Returns:
            matplotlib Figure object
        """
        logger.info("[ImageEditorViewModel] Visualizing analysis result...")
        
        try:
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
                logger.info(f"[ImageEditorViewModel] ✓ Analysis result saved to: {output_path}")
            
            return fig
        except Exception as e:
            logger.error(f"[ImageEditorViewModel] ✗ Visualization error: {str(e)}")
            raise

    def visualize_calibration_result(self, analysis_result, output_path=None):
        """
        Visualize calibration results using matplotlib.
        
        Args:
            analysis_result: DropletAnalysisResult object
            output_path: Visualization image save path
        
        Returns:
            matplotlib Figure object
        """
        logger.info("[ImageEditorViewModel] Visualizing calibration result...")
        
        try:
            fig = self.visualize_result(analysis_result, output_path)
            logger.info("[ImageEditorViewModel] ✓ Visualization completed")
            return fig
        except Exception as e:
            error_msg = f"Visualization error: {str(e)}"
            logger.error(f"[ImageEditorViewModel] ✗ {error_msg}")
            self.error_occurred.emit(error_msg)
            return None