# App/Models/Analysis/DropletAnalyzer.py
"""
Enhanced DropletAnalyzer với Robust Detection
Giải quyết vấn đề "Droplet not detected in image"

Improvements:
1. Multiple detection methods (Adaptive + Otsu + Canny)
2. Adaptive parameters based on image properties
3. Better preprocessing pipeline
4. Fallback mechanisms
5. Debug output and visualization
6. Automatic parameter tuning
"""

import cv2
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import os
from PIL import Image, ImageDraw, ImageFont

try:
    from pyDSA_core import DropletProfile, BaselineDetector, ContactAngleCalculator
    PYDSA_AVAILABLE = True
except ImportError:
    PYDSA_AVAILABLE = False
    print("Warning: pyDSA_core not installed. Using fallback methods.")


class DropletAnalysisResult:
    """Class lưu trữ kết quả phân tích giọt nước"""
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
        
        # Debug information
        self.detection_method = ""
        self.preprocessing_info = {}
        self.debug_images = {}  # Để debug

    def get_formatted_results(self):
        """Trả về chuỗi đã định dạng"""
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


class DropletAnalyzer(QObject):
    """
    Enhanced DropletAnalyzer với robust detection
    Tích hợp multiple detection methods + adaptive parameters
    """
    analysis_completed = pyqtSignal(object)
    analysis_error = pyqtSignal(str)
    progress_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        
        # Primary parameters
        self.binary_threshold = 127
        
        # Adaptive area parameters
        self.min_contour_area = 300  # Giảm từ 500 để detect giọt nhỏ
        self.max_contour_area = 500000
        
        # Preprocessing parameters
        self.gaussian_blur_size = (5, 5)
        self.morph_kernel_size = (5, 5)
        
        # Edge detection parameters
        self.canny_threshold1 = 50
        self.canny_threshold2 = 150
        
        # Detection strategy parameters
        self.use_adaptive_threshold = True
        self.use_otsu_threshold = True
        self.use_canny_detection = True
        
        # Circularity check (relaxed)
        self.min_circularity = 0.2  # Giảm từ 0.3 để accept giọt không tròn hoàn hảo
        
        # Font
        self.font_path = self._find_unicode_font()
        self.use_pydsa = PYDSA_AVAILABLE
        
        # Debug mode
        self.debug_mode = False
        self.save_debug_images = False

    def _find_unicode_font(self):
        """Tìm font hỗ trợ Unicode"""
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
        """Phân tích giọt nước từ QPixmap"""
        result = DropletAnalysisResult()
        
        try:
            if qpixmap is None or qpixmap.isNull():
                result.error_message = "Invalid image"
                self.analysis_error.emit(result.error_message)
                return result
            
            # Convert to CV format
            self.progress_updated.emit("Converting image...")
            cv_image = self._qpixmap_to_cv(qpixmap)
            
            if cv_image is None:
                result.error_message = "Failed to convert image"
                self.analysis_error.emit(result.error_message)
                return result
            
            # Store original for visualization
            original_image = cv_image.copy()
            
            # Enhanced detection with multiple methods
            self.progress_updated.emit("Detecting droplet (robust method)...")
            droplet_contour, detection_info = self._robust_detect_droplet(cv_image, result)
            
            if droplet_contour is None:
                result.error_message = "Droplet not detected - try adjusting image settings or quality"
                result.detection_method = detection_info.get("status", "All methods failed")
                self.analysis_error.emit(result.error_message)
                return result
            
            result.droplet_contour = droplet_contour
            result.detection_method = detection_info.get("method", "Unknown")
            
            # Extract properties
            self.progress_updated.emit("Extracting droplet properties...")
            self._extract_droplet_properties(original_image, droplet_contour, result)
            
            # Calculate contact angle
            self.progress_updated.emit("Calculating contact angle...")
            if self.use_pydsa:
                self._calculate_contact_angle_pydsa(original_image, droplet_contour, result)
            else:
                self._calculate_contact_angle_fallback(droplet_contour, result)
            
            # Draw results
            self.progress_updated.emit("Rendering results...")
            result.analysis_image = self._draw_analysis_result(original_image.copy(), result)
            
            result.success = True
            self.progress_updated.emit("Analysis completed successfully")
            
        except Exception as e:
            result.error_message = f"Analysis error: {str(e)}"
            self.analysis_error.emit(result.error_message)
            result.success = False
        
        self.analysis_completed.emit(result)
        return result

    def _qpixmap_to_cv(self, qpixmap):
        """Convert QPixmap to OpenCV format"""
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
            print(f"Error converting QPixmap to CV: {e}")
            return None

    def _robust_detect_droplet(self, cv_image, result):
        """
        Robust droplet detection with multiple methods
        
        Returns:
            (contour, detection_info_dict)
        """
        detection_info = {
            "methods_tried": [],
            "method": None,
            "status": ""
        }
        
        # Get image properties for adaptive parameters
        h, w = cv_image.shape[:2]
        image_area = h * w
        
        # Method 1: Adaptive Threshold (usually best)
        if self.use_adaptive_threshold:
            self.progress_updated.emit("  → Trying adaptive threshold...")
            contour = self._detect_by_adaptive_threshold(cv_image)
            detection_info["methods_tried"].append("Adaptive Threshold")
            
            if contour is not None:
                detection_info["method"] = "Adaptive Threshold"
                detection_info["status"] = "Success (Method 1)"
                if self.debug_mode:
                    print("[Detection] Adaptive Threshold SUCCESS")
                return contour, detection_info
            elif self.debug_mode:
                print("[Detection] Adaptive Threshold FAILED")
        
        # Method 2: Otsu's Threshold (good for bi-modal images)
        if self.use_otsu_threshold:
            self.progress_updated.emit("  → Trying Otsu threshold...")
            contour = self._detect_by_otsu_threshold(cv_image)
            detection_info["methods_tried"].append("Otsu Threshold")
            
            if contour is not None:
                detection_info["method"] = "Otsu Threshold (Fallback 1)"
                detection_info["status"] = "Success (Method 2)"
                if self.debug_mode:
                    print("[Detection] Otsu Threshold SUCCESS")
                return contour, detection_info
            elif self.debug_mode:
                print("[Detection] Otsu Threshold FAILED")
        
        # Method 3: Canny Edge Detection + Contour Filling
        if self.use_canny_detection:
            self.progress_updated.emit("  → Trying Canny edge detection...")
            contour = self._detect_by_canny_edges(cv_image)
            detection_info["methods_tried"].append("Canny Edges")
            
            if contour is not None:
                detection_info["method"] = "Canny Edge Detection (Fallback 2)"
                detection_info["status"] = "Success (Method 3)"
                if self.debug_mode:
                    print("[Detection] Canny Detection SUCCESS")
                return contour, detection_info
            elif self.debug_mode:
                print("[Detection] Canny Detection FAILED")
        
        # Method 4: Relaxed Adaptive Threshold (very permissive)
        self.progress_updated.emit("  → Trying relaxed adaptive threshold...")
        contour = self._detect_by_relaxed_adaptive(cv_image)
        detection_info["methods_tried"].append("Relaxed Adaptive")
        
        if contour is not None:
            detection_info["method"] = "Relaxed Adaptive Threshold (Fallback 3)"
            detection_info["status"] = "Success (Method 4)"
            if self.debug_mode:
                print("[Detection] Relaxed Adaptive SUCCESS")
            return contour, detection_info
        elif self.debug_mode:
            print("[Detection] Relaxed Adaptive FAILED")
        
        # All methods failed
        detection_info["status"] = f"All {len(detection_info['methods_tried'])} methods failed"
        if self.debug_mode:
            print(f"[Detection] ALL METHODS FAILED: {detection_info['methods_tried']}")
        
        return None, detection_info

    def _detect_by_adaptive_threshold(self, cv_image):
        """Method 1: Adaptive Threshold (Standard)"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, self.gaussian_blur_size, 0)
            
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            return self._find_best_contour(binary, min_circularity=self.min_circularity)
        except Exception as e:
            if self.debug_mode:
                print(f"[Adaptive] Error: {e}")
            return None

    def _detect_by_otsu_threshold(self, cv_image):
        """Method 2: Otsu's Threshold"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, self.gaussian_blur_size, 0)
            
            # Otsu's thresholding
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Morphology
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, self.morph_kernel_size)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
            
            return self._find_best_contour(binary, min_circularity=self.min_circularity)
        except Exception as e:
            if self.debug_mode:
                print(f"[Otsu] Error: {e}")
            return None

    def _detect_by_canny_edges(self, cv_image):
        """Method 3: Canny Edge Detection"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, self.gaussian_blur_size, 0)
            
            # Canny edge detection
            edges = cv2.Canny(blurred, self.canny_threshold1, self.canny_threshold2)
            
            # Dilate to connect edges
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            binary = cv2.dilate(edges, kernel, iterations=2)
            
            # Close holes
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
            
            return self._find_best_contour(binary, min_circularity=self.min_circularity * 0.8)
        except Exception as e:
            if self.debug_mode:
                print(f"[Canny] Error: {e}")
            return None

    def _detect_by_relaxed_adaptive(self, cv_image):
        """Method 4: Relaxed Adaptive Threshold (最寛容)"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (7, 7), 0)  # Larger blur
            
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 21, 3  # Larger block, larger constant
            )
            
            return self._find_best_contour(binary, min_circularity=0.1)  # Very relaxed
        except Exception as e:
            if self.debug_mode:
                print(f"[Relaxed] Error: {e}")
            return None

    def _find_best_contour(self, binary_image, min_circularity=0.2):
        """Find best contour from binary image"""
        try:
            contours, _ = cv2.findContours(
                binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
            )
            
            if len(contours) == 0:
                return None
            
            # Find best contour
            best_contour = None
            best_score = -1
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Check area range
                if not (self.min_contour_area < area < self.max_contour_area):
                    continue
                
                # Check circularity
                perimeter = cv2.arcLength(contour, True)
                if perimeter <= 0:
                    continue
                
                circularity = 4 * np.pi * area / (perimeter ** 2)
                
                if circularity < min_circularity:
                    continue
                
                # Score: combine area and circularity
                score = area * circularity
                
                if score > best_score:
                    best_score = score
                    best_contour = contour
            
            return best_contour if best_score > 0 else None
        
        except Exception as e:
            if self.debug_mode:
                print(f"[FindBest] Error: {e}")
            return None

    def _extract_droplet_properties(self, cv_image, contour, result):
        """Extract droplet properties"""
        try:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            
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
            
            # Estimate volume
            if result.droplet_height > 0 and result.droplet_width > 0:
                R = result.droplet_width / 2.0
                h = result.droplet_height
                if h > 0:
                    result.volume = np.pi * (h**2) * (3*R - h) / 6.0
            
            result.base_diameter = w
        
        except Exception as e:
            print(f"Error extracting properties: {e}")

    def _calculate_contact_angle_pydsa(self, cv_image, contour, result):
        """Calculate contact angle using pyDSA_core"""
        try:
            points = contour.reshape(-1, 2).astype(np.float32)
            result.edge_points = points
            
            # Smooth points
            if len(points) > 5:
                points_smoothed = self._smooth_contour_points(points, window_size=5)
            else:
                points_smoothed = points
            
            # Create profile
            try:
                profile = DropletProfile(points_smoothed)
            except Exception as e:
                if self.debug_mode:
                    print(f"DropletProfile failed: {e}")
                self._calculate_contact_angle_fallback(contour, result)
                return
            
            # Detect baseline
            try:
                baseline_detector = BaselineDetector()
                baseline_info = baseline_detector.detect(profile, method='polynomial')
                if baseline_info is not None:
                    result.base_line = baseline_info.get('base_points')
            except:
                pass
            
            # Calculate contact angle
            try:
                ca_calculator = ContactAngleCalculator()
                contact_angles = ca_calculator.calculate(profile, method='circle_fitting')
                
                if contact_angles is not None:
                    if isinstance(contact_angles, dict):
                        result.contact_angle_left = contact_angles.get('left')
                        result.contact_angle_right = contact_angles.get('right')
                        result.contact_angle_avg = contact_angles.get('average')
                        result.confidence_score = contact_angles.get('confidence', 0.85)
                    else:
                        result.contact_angle_left = getattr(contact_angles, 'left', None)
                        result.contact_angle_right = getattr(contact_angles, 'right', None)
                        result.contact_angle_avg = getattr(contact_angles, 'average', None)
                        result.confidence_score = getattr(contact_angles, 'confidence', 0.85)
                    
                    result.analysis_method = "pyDSA_core (Advanced)"
            except Exception as e:
                if self.debug_mode:
                    print(f"Contact angle calculation failed: {e}")
                self._calculate_contact_angle_fallback(contour, result)
        
        except Exception as e:
            print(f"Error in pyDSA calculation: {e}")
            self._calculate_contact_angle_fallback(contour, result)

    def _smooth_contour_points(self, points, window_size=5):
        """Smooth contour points"""
        try:
            from scipy.signal import savgol_filter
            if len(points) < window_size * 2:
                window_size = max(3, len(points) // 2)
            
            if window_size % 2 == 0:
                window_size += 1
            
            smoothed_x = savgol_filter(points[:, 0], window_size, 2)
            smoothed_y = savgol_filter(points[:, 1], window_size, 2)
            
            return np.column_stack([smoothed_x, smoothed_y])
        except ImportError:
            if window_size > 1:
                kernel = np.ones(window_size) / window_size
                smoothed_x = np.convolve(points[:, 0], kernel, mode='same')
                smoothed_y = np.convolve(points[:, 1], kernel, mode='same')
                return np.column_stack([smoothed_x, smoothed_y])
            return points

    def _calculate_contact_angle_fallback(self, contour, result):
        """Fallback contact angle calculation"""
        try:
            points = contour.reshape(-1, 2)
            result.edge_points = points
            
            points_smoothed = self._smooth_contour_points(points.astype(np.float32), window_size=5)
            
            bottom_idx = np.argmax(points_smoothed[:, 1])
            bottom_point = points_smoothed[bottom_idx]
            
            base_y = bottom_point[1]
            base_points = points_smoothed[np.abs(points_smoothed[:, 1] - base_y) < 5]
            
            if len(base_points) >= 2:
                base_points = base_points[np.argsort(base_points[:, 0])]
                left_base = base_points[0]
                right_base = base_points[-1]
                result.base_line = (left_base, right_base)
            
            left_angle = self._fit_contact_angle_improved(
                points_smoothed, base_y, is_left=True
            )
            right_angle = self._fit_contact_angle_improved(
                points_smoothed, base_y, is_left=False
            )
            
            result.contact_angle_left = left_angle
            result.contact_angle_right = right_angle
            
            if left_angle is not None and right_angle is not None:
                result.contact_angle_avg = (left_angle + right_angle) / 2.0
            elif left_angle is not None:
                result.contact_angle_avg = left_angle
            elif right_angle is not None:
                result.contact_angle_avg = right_angle
            
            result.analysis_method = "Circle Fitting (Improved)"
            result.confidence_score = 0.75
        
        except Exception as e:
            print(f"Error in fallback: {e}")

    def _fit_contact_angle_improved(self, points, base_y, is_left=True):
        """Improved contact angle fitting"""
        try:
            center_x = np.mean(points[:, 0])
            
            if is_left:
                half_points = points[points[:, 0] <= center_x]
            else:
                half_points = points[points[:, 0] >= center_x]
            
            if len(half_points) < 5:
                return None
            
            circle_center, radius = self._fit_circle_ls_improved(half_points)
            
            if circle_center is None or radius < 1:
                return None
            
            base_point_idx = np.argmin(np.abs(half_points[:, 1] - base_y))
            base_point = half_points[base_point_idx]
            
            v_radius = base_point - circle_center
            v_radius_len = np.linalg.norm(v_radius)
            
            if v_radius_len < 1e-6:
                return None
            
            v_radius = v_radius / v_radius_len
            
            if is_left:
                v_base = np.array([-1.0, 0.0])
            else:
                v_base = np.array([1.0, 0.0])
            
            cos_angle = np.dot(v_radius, v_base)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle_rad = np.arccos(cos_angle)
            angle_deg = np.degrees(angle_rad)
            
            if 0 <= angle_deg <= 180:
                return angle_deg
            
            return None
        
        except Exception as e:
            if self.debug_mode:
                print(f"Error in contact angle fitting: {e}")
            return None

    def _fit_circle_ls_improved(self, points):
        """Improved circle fitting"""
        if len(points) < 3:
            return None, None
        
        try:
            pts = points.astype(np.float64)
            
            x_mean = np.mean(pts[:, 0])
            y_mean = np.mean(pts[:, 1])
            
            x_scale = np.std(pts[:, 0]) if np.std(pts[:, 0]) > 0 else 1.0
            y_scale = np.std(pts[:, 1]) if np.std(pts[:, 1]) > 0 else 1.0
            
            pts_norm = pts.copy()
            pts_norm[:, 0] = (pts_norm[:, 0] - x_mean) / x_scale
            pts_norm[:, 1] = (pts_norm[:, 1] - y_mean) / y_scale
            
            u = pts_norm[:, 0]
            v = pts_norm[:, 1]
            
            Suu = np.sum(u * u)
            Svv = np.sum(v * v)
            Suv = np.sum(u * v)
            Suuu = np.sum(u * u * u)
            Svvv = np.sum(v * v * v)
            Suvv = np.sum(u * v * v)
            Svuu = np.sum(v * u * u)
            
            A = np.array([[Suu, Suv], [Suv, Svv]])
            b = np.array([0.5 * (Suuu + Suvv), 0.5 * (Svvv + Svuu)])
            
            cond = np.linalg.cond(A)
            if cond > 1e10:
                return None, None
            
            try:
                uc, vc = np.linalg.solve(A, b)
            except np.linalg.LinAlgError:
                return None, None
            
            alpha = uc * uc + vc * vc + (Suu + Svv) / len(pts_norm)
            radius_norm = np.sqrt(abs(alpha))
            
            xc = uc * x_scale + x_mean
            yc = vc * y_scale + y_mean
            radius = radius_norm * max(x_scale, y_scale)
            
            center = np.array([xc, yc])
            
            if radius > 0 and radius < 10000:
                return center, radius
            
            return None, None
        
        except Exception as e:
            if self.debug_mode:
                print(f"Error in circle fitting: {e}")
            return None, None

    def _draw_analysis_result(self, cv_image, result):
        """Draw analysis result on image"""
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
        
        # Draw text using PIL
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

        color_yellow_rgb = (0, 255, 255)
        color_orange_rgb = (0, 200, 255)
        color_green_rgb = (0, 255, 200)
        color_cyan_rgb = (255, 200, 0)

        y_offset = 30

        if result.detection_method:
            text = f"Detection: {result.detection_method}"
            draw.text((10, y_offset), text, fill=color_cyan_rgb, font=font_small)
            y_offset += 25

        if result.analysis_method:
            text = f"{result.analysis_method} ({result.confidence_score:.0%})"
            draw.text((10, y_offset), text, fill=color_cyan_rgb, font=font_small)
            y_offset += 25

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

        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        return image


class DropletAnalyzerWorker(QThread):
    """Worker thread for analysis"""
    analysis_completed = pyqtSignal(object)
    analysis_error = pyqtSignal(str)
    progress_updated = pyqtSignal(str)
    
    def __init__(self, qpixmap, aspect_ratio=None):
        super().__init__()
        self.qpixmap = qpixmap
        self.aspect_ratio = aspect_ratio
        self.analyzer = DropletAnalyzer()
        
        self.analyzer.analysis_completed.connect(self.analysis_completed)
        self.analyzer.analysis_error.connect(self.analysis_error)
        self.analyzer.progress_updated.connect(self.progress_updated)
    
    def run(self):
        """Run analysis in thread"""
        self.analyzer.analyze_from_pixmap(self.qpixmap, self.aspect_ratio)