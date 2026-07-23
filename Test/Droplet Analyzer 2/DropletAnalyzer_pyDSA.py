# App/Models/Analysis/DropletAnalyzer_pyDSA.py
"""
DropletAnalyzer sử dụng thư viện pyDSA_core để phân tích góc tiếp xúc chính xác.
Nếu pyDSA_core không khả dụng, quá trình phân tích sẽ thất bại và trả về lỗi.
"""

import cv2
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap
import os

# Cố gắng import pyDSA_core, nếu không có thì báo lỗi
try:
    from pyDSA_core import DropletProfile, BaselineDetector, ContactAngleCalculator
    PYDSA_AVAILABLE = True
except ImportError:
    PYDSA_AVAILABLE = False


class DropletAnalysisResult:
    """Kết quả phân tích giọt nước (giống cấu trúc cũ)"""
    def __init__(self):
        self.contact_angle_left = None
        self.contact_angle_right = None
        self.contact_angle_avg = None
        self.droplet_width = None
        self.droplet_height = None
        self.base_diameter = None
        self.volume = None
        self.surface_tension = None
        self.droplet_contour = None
        self.edge_points = None
        self.base_line = None
        self.fitted_circle = None
        self.analysis_image = None
        self.success = False
        self.error_message = ""
        self.analysis_method = ""
        self.confidence_score = 0.0
        self.detection_method = ""

    def get_formatted_results(self):
        """Định dạng kết quả thành chuỗi (giữ nguyên)"""
        lines = []
        if self.success:
            if self.analysis_method:
                lines.append(f"Method: {self.analysis_method}")
                lines.append(f"Confidence: {self.confidence_score:.1%}")
                if self.detection_method:
                    lines.append(f"Detection: {self.detection_method}")
                lines.append("-" * 40)

            if any([self.contact_angle_avg, self.contact_angle_left, self.contact_angle_right]):
                lines.append("Contact Angle Measurements:")
                lines.append("-" * 40)
                if self.contact_angle_avg is not None:
                    lines.append(f"  Average:  {self.contact_angle_avg:.2f}°")
                if self.contact_angle_left is not None:
                    lines.append(f"  Left:     {self.contact_angle_left:.2f}°")
                if self.contact_angle_right is not None:
                    lines.append(f"  Right:    {self.contact_angle_right:.2f}°")
                lines.append("")

            if any([self.droplet_width, self.droplet_height, self.base_diameter]):
                lines.append("Droplet Dimensions:")
                lines.append("-" * 40)
                if self.droplet_width is not None:
                    lines.append(f"  Width:    {self.droplet_width:.2f} px")
                if self.droplet_height is not None:
                    lines.append(f"  Height:   {self.droplet_height:.2f} px")
                if self.base_diameter is not None:
                    lines.append(f"  Base:     {self.base_diameter:.2f} px")
                lines.append("")

            if self.fitted_circle is not None:
                lines.append("Circle Fitting:")
                lines.append("-" * 40)
                lines.append(f"  Major Axis: {self.fitted_circle['major_axis']:.2f} px")
                lines.append(f"  Minor Axis: {self.fitted_circle['minor_axis']:.2f} px")
                lines.append(f"  Angle:      {self.fitted_circle['angle']:.2f}°")
                lines.append("")

            if self.volume is not None:
                lines.append(f"Volume (est.): {self.volume:.2f} units³")
        else:
            lines.append(f"Error: {self.error_message}")

        return "\n".join(lines)


class DropletAnalyzer_pyDSA(QObject):
    """Phân tích giọt nước dựa trên pyDSA_core (bắt buộc phải có thư viện)"""
    analysis_completed = pyqtSignal(object)
    analysis_error = pyqtSignal(str)
    progress_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        if not PYDSA_AVAILABLE:
            raise ImportError("pyDSA_core is not available. Cannot use this analyzer.")
        self.font_path = self._find_unicode_font()
        self.debug_mode = False

    def _find_unicode_font(self):
        possible_paths = [
            "arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def analyze_from_pixmap(self, qpixmap, aspect_ratio=None):
        """Phân tích từ QPixmap, trả về DropletAnalysisResult"""
        result = DropletAnalysisResult()
        try:
            if qpixmap is None or qpixmap.isNull():
                result.error_message = "Invalid image"
                self.analysis_error.emit(result.error_message)
                self.analysis_completed.emit(result)
                return result

            self.progress_updated.emit("Converting image...")
            cv_image = self._qpixmap_to_cv(qpixmap)
            if cv_image is None:
                result.error_message = "Failed to convert image"
                self.analysis_error.emit(result.error_message)
                self.analysis_completed.emit(result)
                return result

            # Phát hiện giọt nước bằng phương pháp đơn giản (adaptive threshold)
            # pyDSA_core có thể tự phát hiện, nhưng ta cung cấp contour để đảm bảo
            self.progress_updated.emit("Detecting droplet...")
            contour = self._detect_simple_contour(cv_image)
            if contour is None:
                result.error_message = "Droplet not detected"
                self.analysis_error.emit(result.error_message)
                self.analysis_completed.emit(result)
                return result

            result.droplet_contour = contour
            result.detection_method = "Adaptive Threshold"

            # Chuẩn bị dữ liệu cho pyDSA
            points = contour.reshape(-1, 2).astype(np.float32)
            result.edge_points = points

            self.progress_updated.emit("Running pyDSA_core analysis...")
            # Sử dụng pyDSA_core để tính góc tiếp xúc
            profile = DropletProfile(points)
            baseline_detector = BaselineDetector()
            baseline_info = baseline_detector.detect(profile, method='polynomial')
            if baseline_info is not None:
                result.base_line = baseline_info.get('base_points')

            ca_calculator = ContactAngleCalculator()
            contact_angles = ca_calculator.calculate(profile, method='circle_fitting')

            if contact_angles is not None:
                if isinstance(contact_angles, dict):
                    result.contact_angle_left = contact_angles.get('left')
                    result.contact_angle_right = contact_angles.get('right')
                    result.contact_angle_avg = contact_angles.get('average')
                    result.confidence_score = contact_angles.get('confidence', 0.95)
                else:
                    result.contact_angle_left = getattr(contact_angles, 'left', None)
                    result.contact_angle_right = getattr(contact_angles, 'right', None)
                    result.contact_angle_avg = getattr(contact_angles, 'average', None)
                    result.confidence_score = getattr(contact_angles, 'confidence', 0.95)

                result.analysis_method = "pyDSA_core (Advanced)"
            else:
                result.error_message = "pyDSA_core returned no contact angles"
                self.analysis_error.emit(result.error_message)
                self.analysis_completed.emit(result)
                return result

            # Tính thêm các thông số phụ trợ
            self._extract_droplet_properties(cv_image, contour, result)

            # Vẽ kết quả
            self.progress_updated.emit("Rendering results...")
            result.analysis_image = self._draw_analysis_result(cv_image.copy(), result)

            result.success = True
            self.progress_updated.emit("Analysis completed successfully")

        except Exception as e:
            result.error_message = f"Analysis error: {str(e)}"
            self.analysis_error.emit(result.error_message)
            result.success = False

        self.analysis_completed.emit(result)
        return result

    def _qpixmap_to_cv(self, qpixmap):
        """Chuyển QPixmap sang ảnh OpenCV BGR"""
        try:
            qimage = qpixmap.toImage()
            width = qimage.width()
            height = qimage.height()
            ptr = qimage.bits()
            ptr.setsize(qimage.sizeInBytes())
            arr = np.array(ptr).reshape(height, width, 4)
            cv_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            return cv_image
        except Exception as e:
            print(f"Error converting QPixmap: {e}")
            return None

    def _detect_simple_contour(self, cv_image):
        """Phát hiện giọt nước bằng adaptive threshold (dùng chung với bên kia)"""
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            return None
        # Chọn contour lớn nhất
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        if area < 300 or area > 500000:
            return None
        return largest

    def _extract_droplet_properties(self, cv_image, contour, result):
        """Trích xuất các thuộc tính cơ bản của giọt nước (giống cũ)"""
        try:
            x, y, w, h = cv2.boundingRect(contour)
            result.droplet_width = w
            result.droplet_height = h
            result.base_diameter = w

            if len(contour) >= 5:
                try:
                    ellipse = cv2.fitEllipse(contour)
                    (cx, cy), (major, minor), angle = ellipse
                    result.fitted_circle = {
                        'center': (cx, cy),
                        'major_axis': major,
                        'minor_axis': minor,
                        'angle': angle
                    }
                except:
                    pass

            if h > 0 and w > 0:
                R = w / 2.0
                result.volume = np.pi * (h**2) * (3*R - h) / 6.0
        except Exception as e:
            print(f"Error extracting properties: {e}")

    def _draw_analysis_result(self, cv_image, result):
        """Vẽ kết quả lên ảnh (giữ nguyên từ code cũ)"""
        image = cv_image.copy()
        if result.droplet_contour is not None:
            cv2.drawContours(image, [result.droplet_contour], 0, (0, 255, 0), 2)
        if result.base_line is not None:
            pt1 = tuple(result.base_line[0].astype(int))
            pt2 = tuple(result.base_line[1].astype(int))
            cv2.line(image, pt1, pt2, (255, 0, 0), 2)
        if result.fitted_circle is not None:
            center = tuple(map(int, result.fitted_circle['center']))
            major = int(result.fitted_circle['major_axis'] / 2)
            minor = int(result.fitted_circle['minor_axis'] / 2)
            angle = int(result.fitted_circle['angle'])
            cv2.ellipse(image, center, (major, minor), angle, 0, 360, (0, 0, 255), 2)

        # Thêm text bằng PIL
        from PIL import Image, ImageDraw, ImageFont
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        try:
            if self.font_path and os.path.exists(self.font_path):
                font_large = ImageFont.truetype(self.font_path, 20)
                font_small = ImageFont.truetype(self.font_path, 16)
            else:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        y_offset = 30
        if result.detection_method:
            draw.text((10, y_offset), f"Detection: {result.detection_method}", fill=(255, 200, 0), font=font_small)
            y_offset += 25
        if result.analysis_method:
            draw.text((10, y_offset), f"{result.analysis_method} ({result.confidence_score:.0%})", fill=(255, 200, 0), font=font_small)
            y_offset += 25
        if result.contact_angle_avg is not None:
            draw.text((10, y_offset), f"Contact Angle: {result.contact_angle_avg:.2f}°", fill=(0, 255, 255), font=font_large)
            y_offset += 35
        if result.contact_angle_left is not None:
            draw.text((10, y_offset), f"Left: {result.contact_angle_left:.2f}°", fill=(0, 200, 255), font=font_small)
            y_offset += 30
        if result.contact_angle_right is not None:
            draw.text((10, y_offset), f"Right: {result.contact_angle_right:.2f}°", fill=(0, 200, 255), font=font_small)
            y_offset += 30
        if result.droplet_width is not None and result.droplet_height is not None:
            draw.text((10, y_offset), f"Size: {result.droplet_width:.0f}x{result.droplet_height:.0f}px", fill=(0, 255, 200), font=font_small)

        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return image