# App/Models/Analysis/DropletAnalyzer_Algorithm.py
"""
DropletAnalyzer sử dụng các thuật toán tự xây dựng (xử lý ảnh + hình học).
Đã cải tiến cách tính góc tiếp xúc dựa trên fitting đường tròn và công thức arccos.
"""

import cv2
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap
import os
from PIL import Image, ImageDraw, ImageFont


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


class DropletAnalyzer_Algorithm(QObject):
    """
    Phân tích giọt nước bằng thuật toán tự xây dựng (xử lý ảnh + fitting đường tròn).
    Không phụ thuộc vào pyDSA_core.
    """
    analysis_completed = pyqtSignal(object)
    analysis_error = pyqtSignal(str)
    progress_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Parameters
        self.min_contour_area = 300
        self.max_contour_area = 500000
        self.gaussian_blur_size = (5, 5)
        self.morph_kernel_size = (5, 5)
        self.canny_threshold1 = 50
        self.canny_threshold2 = 150
        self.use_adaptive_threshold = True
        self.use_otsu_threshold = True
        self.use_canny_detection = True
        self.min_circularity = 0.2
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

            original_image = cv_image.copy()

            # Robust detection (giữ nguyên các phương pháp cũ)
            self.progress_updated.emit("Detecting droplet (robust method)...")
            droplet_contour, detection_info = self._robust_detect_droplet(cv_image, result)
            if droplet_contour is None:
                result.error_message = "Droplet not detected - try adjusting image settings"
                result.detection_method = detection_info.get("status", "All methods failed")
                self.analysis_error.emit(result.error_message)
                self.analysis_completed.emit(result)
                return result

            result.droplet_contour = droplet_contour
            result.detection_method = detection_info.get("method", "Unknown")

            self.progress_updated.emit("Extracting droplet properties...")
            self._extract_droplet_properties(original_image, droplet_contour, result)

            self.progress_updated.emit("Calculating contact angle (improved algorithm)...")
            self._calculate_contact_angle_improved(droplet_contour, result)

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

    # ------------------- Phát hiện giọt (giữ nguyên từ code cũ) -------------------
    def _robust_detect_droplet(self, cv_image, result):
        detection_info = {"methods_tried": [], "method": None, "status": ""}
        if self.use_adaptive_threshold:
            self.progress_updated.emit("  → Trying adaptive threshold...")
            contour = self._detect_by_adaptive_threshold(cv_image)
            detection_info["methods_tried"].append("Adaptive")
            if contour is not None:
                detection_info["method"] = "Adaptive Threshold"
                detection_info["status"] = "Success (Method 1)"
                return contour, detection_info
        if self.use_otsu_threshold:
            self.progress_updated.emit("  → Trying Otsu threshold...")
            contour = self._detect_by_otsu_threshold(cv_image)
            detection_info["methods_tried"].append("Otsu")
            if contour is not None:
                detection_info["method"] = "Otsu Threshold"
                detection_info["status"] = "Success (Method 2)"
                return contour, detection_info
        if self.use_canny_detection:
            self.progress_updated.emit("  → Trying Canny edges...")
            contour = self._detect_by_canny_edges(cv_image)
            detection_info["methods_tried"].append("Canny")
            if contour is not None:
                detection_info["method"] = "Canny Edges"
                detection_info["status"] = "Success (Method 3)"
                return contour, detection_info
        self.progress_updated.emit("  → Trying relaxed adaptive...")
        contour = self._detect_by_relaxed_adaptive(cv_image)
        detection_info["methods_tried"].append("Relaxed")
        if contour is not None:
            detection_info["method"] = "Relaxed Adaptive"
            detection_info["status"] = "Success (Method 4)"
            return contour, detection_info
        detection_info["status"] = f"All {len(detection_info['methods_tried'])} methods failed"
        return None, detection_info

    def _detect_by_adaptive_threshold(self, cv_image):
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, self.gaussian_blur_size, 0)
            binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY_INV, 11, 2)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, self.morph_kernel_size)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
            return self._find_best_contour(binary, min_circularity=self.min_circularity)
        except Exception as e:
            if self.debug_mode: print(f"[Adaptive] Error: {e}")
            return None

    def _detect_by_otsu_threshold(self, cv_image):
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, self.gaussian_blur_size, 0)
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, self.morph_kernel_size)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
            return self._find_best_contour(binary, min_circularity=self.min_circularity)
        except Exception as e:
            if self.debug_mode: print(f"[Otsu] Error: {e}")
            return None

    def _detect_by_canny_edges(self, cv_image):
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, self.gaussian_blur_size, 0)
            edges = cv2.Canny(blurred, self.canny_threshold1, self.canny_threshold2)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            binary = cv2.dilate(edges, kernel, iterations=2)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
            return self._find_best_contour(binary, min_circularity=self.min_circularity * 0.8)
        except Exception as e:
            if self.debug_mode: print(f"[Canny] Error: {e}")
            return None

    def _detect_by_relaxed_adaptive(self, cv_image):
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (7, 7), 0)
            binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY_INV, 21, 3)
            return self._find_best_contour(binary, min_circularity=0.1)
        except Exception as e:
            if self.debug_mode: print(f"[Relaxed] Error: {e}")
            return None

    def _find_best_contour(self, binary_image, min_circularity=0.2):
        try:
            contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if not contours:
                return None
            best_contour = None
            best_score = -1
            for contour in contours:
                area = cv2.contourArea(contour)
                if not (self.min_contour_area < area < self.max_contour_area):
                    continue
                perimeter = cv2.arcLength(contour, True)
                if perimeter <= 0:
                    continue
                circularity = 4 * np.pi * area / (perimeter ** 2)
                if circularity < min_circularity:
                    continue
                score = area * circularity
                if score > best_score:
                    best_score = score
                    best_contour = contour
            return best_contour if best_score > 0 else None
        except Exception as e:
            if self.debug_mode: print(f"[FindBest] Error: {e}")
            return None

    def _extract_droplet_properties(self, cv_image, contour, result):
        """Trích xuất các thuộc tính cơ bản (giữ nguyên)"""
        try:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            x, y, w, h = cv2.boundingRect(contour)
            result.droplet_width = w
            result.droplet_height = h
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
            result.base_diameter = w
        except Exception as e:
            print(f"Error extracting properties: {e}")

    # ------------------- Tính góc tiếp xúc cải tiến -------------------
    def _calculate_contact_angle_improved(self, contour, result):
        """
        Tính góc tiếp xúc dựa trên fitting đường tròn cho nửa trái và nửa phải.
        Công thức: θ = arccos(d / R) với d = y_center - y_base (có dấu)
        """
        try:
            points = contour.reshape(-1, 2).astype(np.float32)
            result.edge_points = points

            # Làm mịn contour
            points_smoothed = self._smooth_contour_points(points, window_size=5)

            # Xác định đường baseline (mặt phẳng đế)
            y_base = self._find_baseline_y(points_smoothed)
            if y_base is None:
                raise ValueError("Could not determine baseline")

            # Xác định điểm tiếp xúc trái và phải gần baseline
            left_contact, right_contact = self._find_contact_points(points_smoothed, y_base)
            if left_contact is None or right_contact is None:
                raise ValueError("Could not find contact points")

            # Lưu baseline để vẽ
            result.base_line = (left_contact, right_contact)

            # Tìm điểm đỉnh (y lớn nhất)
            top_idx = np.argmin(points_smoothed[:, 1])  # vì y tăng xuống dưới, nên đỉnh có y nhỏ nhất
            top_point = points_smoothed[top_idx]

            # Tách contour thành nửa trái và phải dựa trên hoành độ đỉnh
            left_mask = points_smoothed[:, 0] <= top_point[0]
            right_mask = points_smoothed[:, 0] >= top_point[0]
            left_points = points_smoothed[left_mask]
            right_points = points_smoothed[right_mask]

            # Đảm bảo mỗi nửa có đủ điểm
            if len(left_points) < 5 or len(right_points) < 5:
                # Fallback: dùng toàn bộ contour để fit một đường tròn
                center, radius = self._fit_circle_ls_improved(points_smoothed)
                if center is not None and radius > 0:
                    d = center[1] - y_base
                    angle = np.arccos(np.clip(d / radius, -1, 1)) * 180 / np.pi
                    result.contact_angle_left = angle
                    result.contact_angle_right = angle
                    result.contact_angle_avg = angle
                    result.analysis_method = "Single Circle Fit (Fallback)"
                    result.confidence_score = 0.7
                else:
                    # Fallback cuối: dùng công thức chiều cao/đáy
                    width = right_contact[0] - left_contact[0]
                    height = top_point[1] - y_base
                    if width > 0 and height > 0:
                        angle = 2 * np.arctan(2 * height / width) * 180 / np.pi
                        result.contact_angle_left = angle
                        result.contact_angle_right = angle
                        result.contact_angle_avg = angle
                        result.analysis_method = "Height/Width Approximation"
                        result.confidence_score = 0.5
                return

            # Fit circle cho nửa trái
            centerL, radiusL = self._fit_circle_ls_improved(left_points)
            # Fit circle cho nửa phải
            centerR, radiusR = self._fit_circle_ls_improved(right_points)

            # Tính góc cho từng bên
            if centerL is not None and radiusL > 0:
                dL = centerL[1] - y_base
                angleL = np.arccos(np.clip(dL / radiusL, -1, 1)) * 180 / np.pi
                result.contact_angle_left = angleL
            if centerR is not None and radiusR > 0:
                dR = centerR[1] - y_base
                angleR = np.arccos(np.clip(dR / radiusR, -1, 1)) * 180 / np.pi
                result.contact_angle_right = angleR

            # Tính trung bình
            if result.contact_angle_left is not None and result.contact_angle_right is not None:
                result.contact_angle_avg = (result.contact_angle_left + result.contact_angle_right) / 2.0
            elif result.contact_angle_left is not None:
                result.contact_angle_avg = result.contact_angle_left
            elif result.contact_angle_right is not None:
                result.contact_angle_avg = result.contact_angle_right

            result.analysis_method = "Improved Circle Fit (Left/Right)"
            result.confidence_score = 0.85

        except Exception as e:
            if self.debug_mode:
                print(f"Error in improved angle calculation: {e}")

    def _find_baseline_y(self, points, tol=3):
        """
        Tìm baseline (mặt phẳng đế) là giá trị y lớn nhất (thấp nhất trong ảnh)
        hoặc trung bình của các điểm gần đáy.
        """
        # Lấy 10% số điểm có y lớn nhất (gần đáy)
        y_vals = points[:, 1]
        sorted_idx = np.argsort(y_vals)[::-1]  # giảm dần
        n = max(1, len(points) // 10)
        bottom_points = points[sorted_idx[:n]]
        # Loại bỏ các điểm có y quá xa so với trung bình
        mean_y = np.mean(bottom_points[:, 1])
        std_y = np.std(bottom_points[:, 1])
        filtered = bottom_points[np.abs(bottom_points[:, 1] - mean_y) <= 2 * std_y]
        if len(filtered) == 0:
            return mean_y
        return np.mean(filtered[:, 1])

    def _find_contact_points(self, points, y_base, tol=3):
        """Tìm điểm tiếp xúc trái và phải gần baseline"""
        mask = np.abs(points[:, 1] - y_base) <= tol
        candidates = points[mask]
        if len(candidates) < 2:
            return None, None
        left = candidates[np.argmin(candidates[:, 0])]
        right = candidates[np.argmax(candidates[:, 0])]
        return left, right

    def _smooth_contour_points(self, points, window_size=5):
        """Làm mịn contour bằng moving average"""
        if len(points) < window_size:
            return points
        kernel = np.ones(window_size) / window_size
        smoothed_x = np.convolve(points[:, 0], kernel, mode='same')
        smoothed_y = np.convolve(points[:, 1], kernel, mode='same')
        return np.column_stack([smoothed_x, smoothed_y])

    def _fit_circle_ls_improved(self, points):
        """
        Fit đường tròn bằng phương pháp bình phương tối thiểu (cải tiến từ code cũ)
        Trả về (center, radius)
        """
        if len(points) < 3:
            return None, None
        try:
            pts = points.astype(np.float64)
            x_mean = np.mean(pts[:, 0])
            y_mean = np.mean(pts[:, 1])
            # Chuẩn hóa để tránh số lớn
            pts_norm = pts.copy()
            pts_norm[:, 0] -= x_mean
            pts_norm[:, 1] -= y_mean

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

            if np.linalg.cond(A) > 1e10:
                return None, None

            uc, vc = np.linalg.solve(A, b)
            alpha = uc * uc + vc * vc + (Suu + Svv) / len(pts_norm)
            radius_norm = np.sqrt(abs(alpha))

            xc = uc + x_mean
            yc = vc + y_mean
            radius = radius_norm

            if radius > 0 and radius < 10000:
                return np.array([xc, yc]), radius
            return None, None
        except Exception as e:
            if self.debug_mode:
                print(f"Circle fit error: {e}")
            return None, None

    # ------------------- Vẽ kết quả (giữ nguyên) -------------------
    def _draw_analysis_result(self, cv_image, result):
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