# App/Models/Vision/HardwareCameraScan.py
import sys
import cv2
from PyQt6.QtCore import QThread, pyqtSignal

try:
    from pygrabber.dshow_graph import FilterGraph
    PYGRABBER_AVAILABLE = True
except ImportError:
    PYGRABBER_AVAILABLE = False

class HardwareCameraScan(QThread):
    cameras_found_signal = pyqtSignal(list)

    def __init__(self, skip_index=None):
        super().__init__()
        self.skip_index = skip_index

    def run(self):
        available_cameras = []
        scan_success = False  
        
        # --- Helper to check if the index already exists in the list dictionary ---
        def is_index_in_list(idx, camera_list):
            for cam in camera_list:
                if cam['index'] == idx:
                    return True
            return False

        if sys.platform.startswith("win") and PYGRABBER_AVAILABLE:
            try:
                graph = FilterGraph()
                devices = graph.get_input_devices() 
                
                for i, device_name in enumerate(devices):
                    cam_idx = i 
                    
                    if self.skip_index is not None and cam_idx == self.skip_index:
                        if not is_index_in_list(cam_idx, available_cameras):
                            available_cameras.append({"index": cam_idx, "name": device_name})
                        continue
                    
                    if is_index_in_list(cam_idx, available_cameras):
                        continue

                    available_cameras.append({"index": cam_idx, "name": device_name})
                
                scan_success = True 

            except Exception as e:
                print(f"Pygrabber error: {e}")
                scan_success = False 

        if not scan_success:
            for i in range(5): 
                if self.skip_index is not None and i == self.skip_index:
                    if not is_index_in_list(i, available_cameras):
                        available_cameras.append({"index": i, "name": f"Camera {i} (Active)"})
                    continue
                
                if is_index_in_list(i, available_cameras):
                    continue

                cap = None
                try:
                    if sys.platform.startswith("win"):
                        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                    else:
                        cap = cv2.VideoCapture(i)
                        
                    if cap.isOpened():
                        ret, _ = cap.read()
                        if ret:
                            available_cameras.append({"index": i, "name": f"Camera {i}"})
                        else:
                            print(f"Warning: Camera {i} detected but busy/unreadable.")
                except Exception:
                    pass 
                finally:
                    if cap is not None:
                        cap.release()

        self.cameras_found_signal.emit(available_cameras)