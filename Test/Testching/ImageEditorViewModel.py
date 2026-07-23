# App/Presentation/ViewModels/FeatureViewModel/ImageEditorViewModel.py
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap
import os
import sys

# Thêm đường dẫn để import module DropletAnalyzer nếu cần thiết, 
# tùy thuộc vào cấu trúc thư mục gốc của dự án.
# Giả định App là root package.
try:
    from App.Models.Analysis.DropletAnalyzer import DropletAnalyzer
except ImportError:
    # Fallback import nếu chạy test cục bộ không theo structure chuẩn
    try:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))
        from App.Models.Analysis.DropletAnalyzer import DropletAnalyzer
    except ImportError:
        DropletAnalyzer = None

class ImageEditorViewModel(QObject):
    image_loaded = pyqtSignal(QPixmap)
    error_occurred = pyqtSignal(str)
    aspect_ratio_changed = pyqtSignal(object)  # tuple (width, height) or None
    
    # Signal mới: Gửi kết quả phân tích về View (chứa pixmap kết quả và thông số)
    analysis_finished = pyqtSignal(dict)

    def __init__(self, project_name=None, item_name=None):
        super().__init__()
        self.project_name = project_name
        self.item_name = item_name
        self.current_pixmap = None
        self.current_image_path = None # Lưu đường dẫn file để Analyzer đọc
        self.aspect_ratio = None  # None = original, otherwise tuple (w, h)
        
        # Khởi tạo Analyzer
        if DropletAnalyzer:
            self.analyzer = DropletAnalyzer()
        else:
            self.analyzer = None

    def load_image(self, file_path):
        """Load ảnh và lưu đường dẫn file."""
        self.current_image_path = file_path # Cập nhật đường dẫn hiện tại
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

    def analyze_droplet(self):
        """
        Thực hiện phân tích ảnh hiện tại bằng DropletAnalyzer.
        """
        if not self.analyzer:
            self.error_occurred.emit("DropletAnalyzer module is missing.")
            return

        if not self.current_image_path or not os.path.exists(self.current_image_path):
            self.error_occurred.emit("No valid image file found to analyze. Please open an image first.")
            return

        try:
            # Gọi hàm phân tích logic
            # Hàm này trả về dict kết quả và error message (nếu có)
            results, error = self.analyzer.analyze_image(self.current_image_path)
            
            if error:
                self.error_occurred.emit(f"Analysis Error: {error}")
                return

            # Xử lý kết quả: Chuyển bytes image thành QPixmap để hiển thị lên GUI
            if results and "result_image" in results:
                img_data = results["result_image"]
                result_pixmap = QPixmap()
                result_pixmap.loadFromData(img_data)
                
                # Cập nhật pixmap kết quả vào dict để View dễ dùng
                results["result_pixmap"] = result_pixmap
                
                # Update current pixmap của ViewModel thành ảnh kết quả (để user có thể save/zoom)
                self.current_pixmap = result_pixmap
                
                self.analysis_finished.emit(results)
                self.image_loaded.emit(result_pixmap) # Trigger update view
            else:
                self.error_occurred.emit("Unknown error: No result data returned.")

        except Exception as e:
            self.error_occurred.emit(f"Analysis Exception: {str(e)}")

    def set_aspect_ratio(self, ratio_text):
        """
        Thiết lập tỉ lệ khung hình từ chuỗi nhập vào.
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