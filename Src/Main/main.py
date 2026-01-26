import sys
import cv2
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QComboBox, 
                             QVBoxLayout, QWidget, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap

# --- THREAD 1: XỬ LÝ VIDEO ---
class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self._is_running = True

    def run(self):
        # TỐI ƯU 1: Sử dụng CAP_DSHOW trên Windows để mở/đóng nhanh hơn
        # Nếu chạy trên Linux/Mac, có thể bỏ cv2.CAP_DSHOW
        if sys.platform.startswith("win"):
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(self.camera_index)

        # Cài đặt độ phân giải mong muốn (tùy chọn, giúp ảnh nét hơn)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            print(f"Lỗi: Không thể mở camera index {self.camera_index}")
            self._is_running = False
            return

        while self._is_running:
            ret, cv_img = cap.read()
            if ret:
                # Chuyển đổi màu và format
                rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                
                # Scale nhẹ nếu cần, nhưng tốt nhất để QLabel tự scale (setScaledContents) để thread nhẹ hơn
                self.change_pixmap_signal.emit(convert_to_qt_format)
            else:
                break
            # Giảm sleep xuống cực thấp hoặc bỏ để video mượt nhất
            time.sleep(0.01) 

        # QUAN TRỌNG: Giải phóng tài nguyên
        cap.release()
        print(f"Thread: Đã giải phóng Camera {self.camera_index}")

    def stop_camera(self):
        self._is_running = False
        # Không gọi self.wait() ở đây để tránh treo UI. 
        # Ta sẽ đợi tín hiệu 'finished' của QThread.

# --- THREAD 2: QUÉT CAMERA (Để không làm chậm khởi động) ---
class CameraScanThread(QThread):
    cameras_found_signal = pyqtSignal(list)

    def run(self):
        available_cameras = []
        # Quét 5 index đầu tiên
        for i in range(5):
            # Dùng CAP_DSHOW để quét nhanh hơn
            if sys.platform.startswith("win"):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(i)
                
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
        
        self.cameras_found_signal.emit(available_cameras)

# --- GIAO DIỆN CHÍNH ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VCA Optima - Camera Viewer (Optimized)")
        self.resize(800, 600)
        
        self.current_thread = None
        self.pending_camera_index = None # Biến lưu camera index đang đợi để mở

        self.setup_ui()
        
        # Bắt đầu quét camera bằng thread riêng
        self.scan_cameras_async()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # ComboBox
        self.camera_selector = QComboBox()
        self.camera_selector.setPlaceholderText("Đang khởi tạo hệ thống...")
        self.camera_selector.setEnabled(False) # Khóa lại cho đến khi quét xong
        self.camera_selector.currentIndexChanged.connect(self.request_camera_change)
        layout.addWidget(self.camera_selector)

        # Label hiển thị Video
        self.image_label = QLabel("Đang tải danh sách Camera...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #555; background-color: #222; color: #AAA;")
        self.image_label.setMinimumSize(640, 480)
        # Cho phép QLabel tự co giãn hình ảnh -> Thread không cần resize -> Nhanh hơn
        self.image_label.setScaledContents(True) 
        layout.addWidget(self.image_label)

    def scan_cameras_async(self):
        """Khởi động thread quét camera"""
        self.scan_thread = CameraScanThread()
        self.scan_thread.cameras_found_signal.connect(self.on_scan_finished)
        self.scan_thread.start()

    def on_scan_finished(self, cameras):
        """Được gọi khi thread quét xong"""
        self.camera_selector.clear()
        
        if not cameras:
            self.image_label.setText("Không tìm thấy Camera nào!")
            self.camera_selector.addItem("No Camera Found")
        else:
            self.image_label.setText("Chọn Camera để bắt đầu")
            # Ngắt tín hiệu để tránh trigger sự kiện khi đang add item
            self.camera_selector.blockSignals(True)
            for idx in cameras:
                self.camera_selector.addItem(f"Camera Index {idx}", idx)
            self.camera_selector.blockSignals(False)
            
            self.camera_selector.setEnabled(True)
            self.camera_selector.setPlaceholderText("Chọn Camera...")
            
            # Tự động chọn camera đầu tiên
            if len(cameras) > 0:
                self.request_camera_change(0)

    def request_camera_change(self, index):
        """
        Hàm điều phối việc đổi camera.
        Thay vì dừng rồi mở ngay (gây lỗi), ta dừng thread cũ và ĐỢI nó kết thúc.
        """
        if index == -1: return
        
        target_cam_idx = self.camera_selector.itemData(index)
        if target_cam_idx is None: return

        print(f"Yêu cầu chuyển sang Camera {target_cam_idx}")

        # Nếu đang có thread chạy
        if self.current_thread is not None and self.current_thread.isRunning():
            # Lưu lại index muốn mở
            self.pending_camera_index = target_cam_idx
            
            # Khóa ComboBox để user không bấm loạn xạ
            self.camera_selector.setEnabled(False)
            self.image_label.setText("Đang chuyển đổi Camera...")
            
            # Ngắt kết nối cũ để không cập nhật ảnh nữa
            try:
                self.current_thread.change_pixmap_signal.disconnect()
            except:
                pass

            # Kết nối tín hiệu finished -> gọi hàm start_pending_camera
            self.current_thread.finished.connect(self.start_pending_camera)
            
            # Ra lệnh dừng (Non-blocking)
            self.current_thread.stop_camera()
        else:
            # Nếu chưa có thread nào chạy, mở luôn
            self.start_camera_thread(target_cam_idx)

    @pyqtSlot()
    def start_pending_camera(self):
        """Được gọi tự động khi thread cũ đã thực sự kết thúc (finished)"""
        print("Thread cũ đã đóng hoàn toàn.")
        
        # Mở khóa lại ComboBox
        self.camera_selector.setEnabled(True)
        
        if self.pending_camera_index is not None:
            self.start_camera_thread(self.pending_camera_index)
            self.pending_camera_index = None

    def start_camera_thread(self, cam_idx):
        """Khởi tạo và chạy thread mới"""
        print(f"Đang khởi động Camera {cam_idx}...")
        self.current_thread = CameraThread(cam_idx)
        self.current_thread.change_pixmap_signal.connect(self.update_image)
        self.current_thread.start()

    @pyqtSlot(QImage)
    def update_image(self, qt_img):
        self.image_label.setPixmap(QPixmap.fromImage(qt_img))

    def closeEvent(self, event):
        """Dọn dẹp khi tắt app"""
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.stop_camera()
            # Ở đây ta cần wait() để đảm bảo thoát sạch, vì app sắp đóng rồi nên wait cũng không sao
            self.current_thread.wait() 
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())