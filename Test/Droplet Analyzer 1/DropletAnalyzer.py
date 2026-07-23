# App/Models/Analysis/DropletAnalyzer.py
import cv2
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import os

# Thêm Pillow để vẽ Unicode
from PIL import Image, ImageDraw, ImageFont


class DropletAnalysisResult:
    """Class lưu trữ kết quả phân tích giọt nước"""
    def __init__(self):
        self.contact_angle_left = None      # Góc contact bên trái (độ)
        self.contact_angle_right = None     # Góc contact bên phải (độ)
        self.contact_angle_avg = None       # Góc contact trung bình (độ)
        self.droplet_width = None           # Chiều rộng giọt (pixel)
        self.droplet_height = None          # Chiều cao giọt (pixel)
        self.base_diameter = None           # Đường kính đáy giọt (pixel)
        self.volume = None                  # Thể tích ước tính (tương đối)
        self.surface_tension = None         # Sự căng bề mặt ước tính
        self.droplet_contour = None         # Contour của giọt nước
        self.edge_points = None             # Các điểm biên của giọt
        self.base_line = None               # Đường base line
        self.fitted_circle = None           # Thông tin vòng tròn fit
        self.analysis_image = None          # Ảnh sau khi phân tích (numpy)
        self.success = False
        self.error_message = ""

    def get_formatted_results(self):
        """
        Trả về chuỗi đã định dạng chứa tất cả kết quả phân tích.
        Dùng chung cho cả ViewModel và Dialog.
        """
        lines = []
        if self.success:
            # Contact Angles
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

            # Droplet Dimensions
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

            # Circle Fitting
            if self.fitted_circle is not None:
                lines.append("Circle Fitting:")
                lines.append("-" * 40)
                lines.append(f"  Major Axis: {self.fitted_circle['major_axis']:.2f} px")
                lines.append(f"  Minor Axis: {self.fitted_circle['minor_axis']:.2f} px")
                lines.append(f"  Angle:      {self.fitted_circle['angle']:.2f}°")
                lines.append("")

            # Volume
            if self.volume is not None:
                lines.append(f"Volume (est.): {self.volume:.2f} units³")
        else:
            lines.append(f"Error: {self.error_message}")

        return "\n".join(lines)


class DropletAnalyzer(QObject):
    """
    Class phân tích giọt nước từ ảnh.
    Sử dụng các thuật toán xử lý ảnh để detect giọt và tính contact angle.
    """
    analysis_completed = pyqtSignal(object)  # Emit DropletAnalysisResult
    analysis_error = pyqtSignal(str)
    progress_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.binary_threshold = 127
        self.min_contour_area = 500
        self.max_contour_area = 500000
        self.gaussian_blur_size = (5, 5)
        self.morph_kernel_size = (5, 5)
        
        # Đường dẫn font hỗ trợ Unicode (có thể chỉnh lại cho phù hợp với hệ thống)
        # Nếu không tìm thấy, sẽ dùng font mặc định của PIL (có thể không hỗ trợ)
        self.font_path = self._find_unicode_font()

    def _find_unicode_font(self):
        """Tìm font hỗ trợ Unicode trên hệ thống (ưu tiên Arial)"""
        possible_paths = [
            "arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None  # fallback to default font

    def analyze_from_pixmap(self, qpixmap, aspect_ratio=None):
        """
        Phân tích giọt nước từ QPixmap.
        
        Args:
            qpixmap: QPixmap chứa ảnh giọt nước
            aspect_ratio: Tuple (width_ratio, height_ratio) để calibrate
        
        Returns:
            DropletAnalysisResult object
        """
        result = DropletAnalysisResult()
        
        try:
            if qpixmap is None or qpixmap.isNull():
                result.error_message = "Invalid image"
                self.analysis_error.emit(result.error_message)
                return result
            
            # Chuyển QPixmap sang OpenCV format
            self.progress_updated.emit("Converting image...")
            cv_image = self._qpixmap_to_cv(qpixmap)
            
            if cv_image is None:
                result.error_message = "Failed to convert image"
                self.analysis_error.emit(result.error_message)
                return result
            
            # Xử lý ảnh
            self.progress_updated.emit("Processing image...")
            processed_image = self._preprocess_image(cv_image)
            
            # Phát hiện giọt nước
            self.progress_updated.emit("Detecting droplet...")
            droplet_contour = self._detect_droplet(processed_image)
            
            if droplet_contour is None:
                result.error_message = "Droplet not detected in image"
                self.analysis_error.emit(result.error_message)
                return result
            
            result.droplet_contour = droplet_contour
            
            # Trích xuất thông tin giọt
            self.progress_updated.emit("Extracting droplet properties...")
            self._extract_droplet_properties(cv_image, droplet_contour, result)
            
            # Tính contact angle
            self.progress_updated.emit("Calculating contact angle...")
            self._calculate_contact_angle(droplet_contour, result)
            
            # Vẽ kết quả lên ảnh
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
        """Chuyển QPixmap sang OpenCV format (numpy array BGR)"""
        try:
            # Chuyển QPixmap sang QImage
            qimage = qpixmap.toImage()
            width = qimage.width()
            height = qimage.height()
            
            # Lấy dữ liệu pixel
            ptr = qimage.bits()
            ptr.setsize(qimage.sizeInBytes())
            arr = np.array(ptr).reshape(height, width, 4)  # RGBA
            
            # Chuyển RGBA sang BGR cho OpenCV
            cv_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            return cv_image
        except Exception as e:
            print(f"Error converting QPixmap to CV: {e}")
            return None

    def _preprocess_image(self, cv_image):
        """
        Tiền xử lý ảnh: 
        - Chuyển sang grayscale
        - Gaussian blur
        - Threshold
        - Morphological operations
        """
        # Chuyển sang grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Gaussian blur để giảm noise
        blurred = cv2.GaussianBlur(gray, self.gaussian_blur_size, 0)
        
        # Adaptive threshold để detect giọt trên các nền khác nhau
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Morphological operations để clean up
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, self.morph_kernel_size
        )
        
        # Closing: fill small holes
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Opening: remove small noise
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        
        return binary

    def _detect_droplet(self, binary_image):
        """
        Phát hiện giọt nước từ ảnh binary.
        Tìm contour lớn nhất trong ảnh.
        """
        contours, _ = cv2.findContours(
            binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        
        if len(contours) == 0:
            return None
        
        # Tìm contour lớn nhất (giọt nước)
        largest_contour = None
        max_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_contour_area < area < self.max_contour_area:
                if area > max_area:
                    max_area = area
                    largest_contour = contour
        
        return largest_contour

    def _extract_droplet_properties(self, cv_image, contour, result):
        """Trích xuất các tính chất của giọt nước"""
        # Tính diện tích và chu vi
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        # Fit bounding box
        x, y, w, h = cv2.boundingRect(contour)
        result.droplet_width = w
        result.droplet_height = h
        
        # Fit ellipse
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
        
        # Tính thể tích ước tính (assuming spherical cap)
        if result.droplet_height > 0 and result.droplet_width > 0:
            # Volume ≈ π * h² * (3*R - h) / 6, where R = width/2
            R = result.droplet_width / 2.0
            h = result.droplet_height
            if h > 0:
                result.volume = np.pi * (h**2) * (3*R - h) / 6.0
        
        result.base_diameter = w

    def _calculate_contact_angle(self, contour, result):
        """
        Tính contact angle từ contour của giọt.
        Sử dụng phương pháp: 
        1. Tìm base line (bottom tangent)
        2. Fit circle vào upper portion
        3. Tính angle giữa circle radius và base line
        """
        try:
            # Lấy các điểm biên của contour
            points = contour.reshape(-1, 2)
            result.edge_points = points
            
            # Tìm điểm đáy (y lớn nhất) - đây là base line
            bottom_idx = np.argmax(points[:, 1])
            bottom_point = points[bottom_idx]
            
            # Tìm hai điểm base line (trái và phải của bottom)
            base_y = bottom_point[1]
            base_points = points[np.abs(points[:, 1] - base_y) < 5]
            
            if len(base_points) >= 2:
                base_points = base_points[np.argsort(base_points[:, 0])]
                left_base = base_points[0]
                right_base = base_points[-1]
                result.base_line = (left_base, right_base)
            
            # Tách upper portion và lower portion
            upper_points = points[points[:, 1] < base_y - (base_y - points[:, 1].min()) * 0.5]
            
            # Fit circle vào upper portion
            if len(upper_points) >= 3:
                # Sử dụng least squares circle fitting
                left_contact_angle = self._fit_contact_angle(
                    points, base_y, is_left=True
                )
                right_contact_angle = self._fit_contact_angle(
                    points, base_y, is_left=False
                )
                
                result.contact_angle_left = left_contact_angle
                result.contact_angle_right = right_contact_angle
                
                if left_contact_angle is not None and right_contact_angle is not None:
                    result.contact_angle_avg = (left_contact_angle + right_contact_angle) / 2.0
                elif left_contact_angle is not None:
                    result.contact_angle_avg = left_contact_angle
                elif right_contact_angle is not None:
                    result.contact_angle_avg = right_contact_angle
        
        except Exception as e:
            print(f"Error calculating contact angle: {e}")

    def _fit_contact_angle(self, points, base_y, is_left=True):
        """
        Fit contact angle từ một phía của giọt.
        
        Phương pháp:
        1. Lấy nửa trái (hoặc phải) của giọt
        2. Fit circle vào nửa đó
        3. Tính angle từ center của circle đến base point
        """
        try:
            # Tìm center x
            center_x = np.mean(points[:, 0])
            
            if is_left:
                # Lấy nửa trái
                half_points = points[points[:, 0] <= center_x]
            else:
                # Lấy nửa phải
                half_points = points[points[:, 0] >= center_x]
            
            if len(half_points) < 3:
                return None
            
            # Fit circle bằng least squares
            circle_center, radius = self._fit_circle_ls(half_points)
            
            if circle_center is None:
                return None
            
            # Tìm base point (điểm gần base_y nhất)
            base_point_idx = np.argmin(np.abs(half_points[:, 1] - base_y))
            base_point = half_points[base_point_idx]
            
            # Vector từ circle center đến base point
            v_radius = base_point - circle_center
            
            # Vector horizontal (base line direction)
            if is_left:
                v_base = np.array([-1.0, 0.0])  # Pointing left
            else:
                v_base = np.array([1.0, 0.0])   # Pointing right
            
            # Tính angle
            cos_angle = np.dot(v_radius, v_base) / (np.linalg.norm(v_radius) + 1e-6)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle_rad = np.arccos(cos_angle)
            angle_deg = np.degrees(angle_rad)
            
            return angle_deg
        
        except Exception as e:
            print(f"Error in _fit_contact_angle: {e}")
            return None

    def _fit_circle_ls(self, points):
        """
        Fit circle vào điểm bằng least squares method.
        Trả về (center, radius) hoặc (None, None) nếu thất bại
        """
        if len(points) < 3:
            return None, None
        
        try:
            # Convert to float
            pts = points.astype(np.float64)
            
            # Mean coordinates
            x_m = np.mean(pts[:, 0])
            y_m = np.mean(pts[:, 1])
            
            # Calculate u and v
            u = pts[:, 0] - x_m
            v = pts[:, 1] - y_m
            
            # Set up least squares system
            Suu = np.sum(u * u)
            Svv = np.sum(v * v)
            Suv = np.sum(u * v)
            Suuu = np.sum(u * u * u)
            Svvv = np.sum(v * v * v)
            Suvv = np.sum(u * v * v)
            Svuu = np.sum(v * u * u)
            
            # Solve system
            A = np.array([[Suu, Suv], [Suv, Svv]])
            b = np.array([0.5 * (Suuu + Suvv), 0.5 * (Svvv + Svuu)])
            
            try:
                uc, vc = np.linalg.solve(A, b)
            except np.linalg.LinAlgError:
                return None, None
            
            # Center coordinates
            xc = uc + x_m
            yc = vc + y_m
            
            # Calculate radius
            alpha = uc * uc + vc * vc + (Suu + Svv) / len(pts)
            radius = np.sqrt(abs(alpha))
            
            center = np.array([xc, yc])
            return center, radius
        
        except Exception as e:
            print(f"Error in circle fitting: {e}")
            return None, None

    def _draw_analysis_result(self, cv_image, result):
        """Vẽ kết quả phân tích lên ảnh (sử dụng PIL để hỗ trợ Unicode)"""
        image = cv_image.copy()
        
        # Vẽ contour, baseline, ellipse vẫn dùng OpenCV (vẽ hình học)
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
        
        # --- Vẽ text bằng PIL để hỗ trợ ký tự "°" ---
        # Chuyển OpenCV BGR sang PIL RGB
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)

        # Xác định font chữ (nếu không tìm thấy font, dùng default – có thể không hiển thị °)
        try:
            if self.font_path and os.path.exists(self.font_path):
                # Ánh xạ font_scale của OpenCV sang cỡ chữ (point)
                # 0.7 -> 20, 0.6 -> 16 (có thể điều chỉnh)
                font_large = ImageFont.truetype(self.font_path, 20)
                font_small = ImageFont.truetype(self.font_path, 16)
            else:
                # Fallback: dùng font default (có thể không hỗ trợ Unicode)
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Màu sắc chuyển từ BGR sang RGB
        color_yellow_rgb = (0, 255, 255)      # (B=255,G=255,R=0) -> (R=0,G=255,B=255)
        color_orange_rgb = (0, 200, 255)      # (B=255,G=200,R=0) -> (R=0,G=200,B=255)
        color_green_rgb = (0, 255, 200)       # (B=200,G=255,R=0) -> (R=0,G=255,B=200)

        y_offset = 30
        h, w = image.shape[:2]

        if result.contact_angle_avg is not None:
            text = f"Contact Angle: {result.contact_angle_avg:.2f}°"
            draw.text((10, y_offset), text, fill=color_yellow_rgb, font=font_large)
            y_offset += 35

        if result.contact_angle_left is not None:
            text = f"Left: {result.contact_angle_left:.2f}°"
            draw.text((10, y_offset), text, fill=color_orange_rgb, font=font_small)
            y_offset += 30

        if result.contact_angle_right is not None:
            text = f"Right: {result.contact_angle_right:.2f}°"
            draw.text((10, y_offset), text, fill=color_orange_rgb, font=font_small)
            y_offset += 30

        if result.droplet_width is not None and result.droplet_height is not None:
            text = f"Size: {result.droplet_width:.0f}x{result.droplet_height:.0f}px"
            draw.text((10, y_offset), text, fill=color_green_rgb, font=font_small)

        # Chuyển PIL Image trở lại OpenCV BGR
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        return image


class DropletAnalyzerWorker(QThread):
    """
    Worker thread để chạy phân tích droplet mà không block UI.
    """
    analysis_completed = pyqtSignal(object)
    analysis_error = pyqtSignal(str)
    progress_updated = pyqtSignal(str)
    
    def __init__(self, qpixmap, aspect_ratio=None):
        super().__init__()
        self.qpixmap = qpixmap
        self.aspect_ratio = aspect_ratio
        self.analyzer = DropletAnalyzer()
        
        # Connect analyzer signals
        self.analyzer.analysis_completed.connect(self.analysis_completed)
        self.analyzer.analysis_error.connect(self.analysis_error)
        self.analyzer.progress_updated.connect(self.progress_updated)
    
    def run(self):
        """Chạy phân tích trong thread"""
        self.analyzer.analyze_from_pixmap(self.qpixmap, self.aspect_ratio)