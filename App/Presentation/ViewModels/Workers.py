# App/Presentation/ViewModels/Workers.py
import os
from PyQt6.QtCore import QThread, pyqtSignal

class FileOperationWorker(QThread):
    """
    Worker handling heavy file operations (Copy/Paste/Move Folder).
    Supports parallel execution via the list management in MainWindow.
    """
    # Signal: (success, message, new_item_name, action_type, target_project)
    sig_finished = pyqtSignal(bool, str, str, str, str)

    def __init__(self, project_manager, src_project, src_folder, target_project, action_type):
        super().__init__()
        self.pm = project_manager
        self.src_project = src_project
        self.src_folder = src_folder
        self.target_project = target_project
        self.action_type = action_type 

    def run(self):
        try:
            if self.action_type == 'COPY':
                success, msg, new_name = self.pm.copy_item_structure(
                    self.src_project, self.src_folder, self.target_project
                )
            elif self.action_type == 'CUT':
                success, msg, new_name = self.pm.move_item_structure(
                    self.src_project, self.src_folder, self.target_project
                )
            else:
                success, msg, new_name = False, "Unknown Action", ""

            self.sig_finished.emit(success, msg, new_name, self.action_type, self.target_project)
            
        except Exception as e:
            self.sig_finished.emit(False, str(e), "", self.action_type, self.target_project)

class FileMediaWorker(QThread):
    """
    Worker handling copy/cut of media files.
    """
    # Signal: (success, message, new_file_name, action_type, target_project, target_item, target_media)
    sig_finished = pyqtSignal(bool, str, str, str, str, str, str)

    def __init__(self, project_manager,
                 src_project, src_item, src_media, src_file,
                 dst_project, dst_item, dst_media, action_type):
        super().__init__()
        self.pm = project_manager
        self.src_project = src_project
        self.src_item = src_item
        self.src_media = src_media
        self.src_file = src_file
        self.dst_project = dst_project
        self.dst_item = dst_item
        self.dst_media = dst_media
        self.action_type = action_type  # 'COPY' or 'CUT'

    def run(self):
        try:
            if self.action_type == 'COPY':
                success, msg, new_name = self.pm.copy_file(
                    self.src_project, self.src_item, self.src_media, self.src_file,
                    self.dst_project, self.dst_item, self.dst_media
                )
            elif self.action_type == 'CUT':
                success, msg, new_name = self.pm.move_file(
                    self.src_project, self.src_item, self.src_media, self.src_file,
                    self.dst_project, self.dst_item, self.dst_media
                )
            else:
                success, msg, new_name = False, "Unknown Action", ""

            self.sig_finished.emit(success, msg, new_name, self.action_type,
                                   self.dst_project, self.dst_item, self.dst_media)
        except Exception as e:
            self.sig_finished.emit(False, str(e), "", self.action_type,
                                   self.dst_project, self.dst_item, self.dst_media)

class FileLoaderWorker(QThread):
    """
    Worker for reading large text/code file contents.
    """
    sig_loaded = pyqtSignal(bool, str, str, str, str) # success, content, file_name, project_name, full_path

    def __init__(self, full_path, project_name):
        super().__init__()
        self.full_path = full_path
        self.project_name = project_name

    def run(self):
        try:
            file_size = os.path.getsize(self.full_path)
            # Limit to 20MB for text files to avoid memory overflow when loading many files simultaneously
            if file_size > 20 * 1024 * 1024: 
                self.sig_loaded.emit(False, "File too large (>20MB)", "", "", "")
                return

            with open(self.full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_name = os.path.basename(self.full_path)
            self.sig_loaded.emit(True, content, file_name, self.project_name, self.full_path)
            
        except UnicodeDecodeError:
             self.sig_loaded.emit(False, "Binary or non-UTF8 file detected.", "", "", "")
        except Exception as e:
             self.sig_loaded.emit(False, str(e), "", "", "")

class VisionWorker(QThread):
    """
    Worker for Vision algorithm processing.
    Use this class to receive raw images, process them, and return results without freezing the UI.
    """
    sig_result_ready = pyqtSignal(object)

    def __init__(self, image_data, algorithm_params):
        super().__init__()
        self.image = image_data
        self.params = algorithm_params

    def run(self):
        # --- VISION ALGORITHM HERE ---    
        result = {"status": "done", "data": []}
        self.sig_result_ready.emit(result)