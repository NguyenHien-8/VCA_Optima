from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, 
                             QFileDialog, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap

from App.Gui.MenuBar import MenuBar
from Vision.CameraManager import CameraManager
from App.Gui.Widgets.MenuBar.ToggleSideBar import ProjectSidebar
from App.Core.ProjectManager import ProjectManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TNH Optima")
        self.resize(1000, 700)

        self.project_manager = ProjectManager()
        self.untitled_count = 1  # [NEW] Đếm số lượng project chưa đặt tên

        # --- SIDEBAR SETUP ---
        self.sidebar = ProjectSidebar(self)
        self.sidebar.setVisible(True) 
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar)
        
        # --- MENU BAR ---
        self.menu_bar_manager = MenuBar(self)
        self.setMenuBar(self.menu_bar_manager)

        # --- LOGIC ---
        self.camera_manager = CameraManager()
        
        self.setup_ui()
        self.connect_signals()
        self.connect_sidebar_signals()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.image_label = QLabel("Waiting for Camera...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #B0B0B0; background-color: #C8C8C8; color: #333333; font-size: 25px;")
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setScaledContents(True) 
        main_layout.addWidget(self.image_label)

    def connect_signals(self):
        self.camera_manager.frame_received_signal.connect(self.update_image)
        self.camera_manager.error_occurred_signal.connect(self.show_error)

    def connect_sidebar_signals(self):
        self.sidebar.sig_new_file.connect(self.action_new_file)
        self.sidebar.sig_delete.connect(self.action_delete_project)
        self.sidebar.sig_rename.connect(self.action_rename_project)
        self.sidebar.sig_save.connect(self.action_save_project)
        self.sidebar.sig_save_as.connect(self.action_save_as_project) # [NEW]
        self.sidebar.sig_close_proj.connect(self.action_close_project)

    # --- ACTION HANDLERS ---

    def handle_create_project(self):
        """
        [UPDATED] Được gọi từ Menu -> File -> New -> New Project
        Tạo project với tên mặc định, không hỏi Save As ngay.
        """
        default_name = f"Untitled-{self.untitled_count}"
        
        try:
            # Tạo project ở Temp path (Logic bên trong ProjectManager)
            self.project_manager.create_project(default_name, specific_path=None)
            
            # Cập nhật UI
            self.sidebar.add_project_item(default_name)
            
            # Tăng biến đếm
            self.untitled_count += 1
            
            # [NOTE] Đã tắt thông báo thành công (QMessageBox.information)
            print(f"Created temp project: {default_name}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def handle_create_file_in_active_project(self):
        """New File (Ctrl+N)"""
        current_project = self.sidebar.get_current_project()
        if current_project:
            self.action_new_file(current_project)
        else:
            QMessageBox.warning(self, "Warning", "Please select a project first.")

    def handle_save_as_project(self):
        """
        [NEW] Được gọi từ Menu -> File -> Save As...
        Lấy project đang chọn và thực hiện Save As.
        """
        current_project = self.sidebar.get_current_project()
        if current_project:
            self.action_save_as_project(current_project)
        else:
            QMessageBox.warning(self, "Warning", "Please select a project to Save As.")

    # --- CONTEXT MENU LOGIC HANDLERS ---

    def action_new_file(self, project_name):
        file_name, ok = QInputDialog.getText(self, "New File", f"Create file in '{project_name}':")
        if ok and file_name:
            success, msg_or_path = self.project_manager.create_file(project_name, file_name)
            if success:
                # [FIXED] Hiển thị file lên TreeView ngay lập tức
                self.sidebar.add_file_item(project_name, file_name)
                # [NOTE] Đã tắt thông báo thành công
            else:
                QMessageBox.warning(self, "Error", msg_or_path)

    def action_save_as_project(self, project_name):
        """
        [NEW] Logic thực hiện Save As: Di chuyển từ Temp -> Real Folder
        """
        # 1. Hỏi người dùng lưu ở đâu
        folder = QFileDialog.getExistingDirectory(self, "Select Directory to Save Project")
        if not folder: return

        # 2. Gọi Manager di chuyển
        success, msg = self.project_manager.save_project_as(project_name, folder)
        
        if success:
            QMessageBox.information(self, "Saved", f"Project '{project_name}' saved to:\n{msg}")
            # Ở đây không cần cập nhật UI Sidebar vì tên không đổi, chỉ đường dẫn ngầm đổi
        else:
            QMessageBox.warning(self, "Error", msg)

    def action_delete_project(self, project_name):
        reply = QMessageBox.question(self, "Delete Project", 
                                     f"Delete '{project_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.project_manager.delete_project(project_name)
            if success:
                self.sidebar.remove_project_item(project_name)
            else:
                QMessageBox.warning(self, "Error", msg)

    def action_rename_project(self, project_name):
        new_name, ok = QInputDialog.getText(self, "Rename Project", "New Name:", text=project_name)
        if ok and new_name and new_name != project_name:
            success, msg = self.project_manager.rename_project(project_name, new_name)
            if success:
                self.sidebar.rename_project_item(project_name, new_name)
            else:
                QMessageBox.warning(self, "Error", msg)

    def action_save_project(self, project_name):
        # Save thường (Ctrl+S)
        self.project_manager.save_project(project_name)
        print(f"Project '{project_name}' saved logic executed.")

    def action_close_project(self, project_name):
        self.sidebar.remove_project_item(project_name)

    # --- EXISTING SLOTS ---
    @pyqtSlot(QImage)
    def update_image(self, qt_img):
        self.image_label.setPixmap(QPixmap.fromImage(qt_img))

    @pyqtSlot(str)
    def show_error(self, message):
        self.image_label.setText(f"LỖI: {message}")
    
    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()