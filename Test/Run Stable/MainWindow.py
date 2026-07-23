# App/Gui/MainWindow.py
import os
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, 
                             QFileDialog, QInputDialog, QMessageBox, QDialog, QStatusBar,
                             QDockWidget) 
from PyQt6.QtCore import Qt, pyqtSlot, QFileInfo
from PyQt6.QtGui import QImage

from Vision.CameraManager import CameraManager
from Controllers.HardwareManager import HardwareManager
from App.Gui.MenuBar import MenuBar
from App.Gui.Widgets.SideBar import ProjectSidebar
from App.Gui.Widgets.StatusBar import StatusBar
from App.Core.ProjectManager import ProjectManager
from App.Gui.TreeviewControl import EditorWorkspace 
from App.Gui.Dialog.DeleteResourcesDialog import DeleteResourcesDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TNH Optima")
        self.resize(1000, 700)

        # --- LOGIC ---
        self.camera_manager = CameraManager()
        self.hardware_manager = HardwareManager()
        self.project_manager = ProjectManager()
        self.untitled_count = 1
        self.clipboard_data = None 
        
        # --- SIDEBAR SETUP ---
        self.sidebar = ProjectSidebar(self)
        
        # Đảm bảo DockWidget có tính năng đóng (Closable) và tách rời (Floatable)
        self.sidebar.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable | 
                                 QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                                 QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.sidebar.setVisible(True) 
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar)
        
        # --- MENU BAR ---
        self.menu_bar_manager = MenuBar(self)
        self.setMenuBar(self.menu_bar_manager)

        # --- STATUS BAR ---
        self.system_status_bar = QStatusBar()
        self.setStatusBar(self.system_status_bar)
        
        # Widget StatusBar custom (nếu có logic riêng)
        self.status_bar = StatusBar() 
        self.system_status_bar.addWidget(self.status_bar, 1) 
        self.system_status_bar.setContentsMargins(0, 0, 0, 0)

        self.setup_ui()
        self.connect_signals()
        self.connect_sidebar_signals()

    def setup_ui(self):     
        icon_close = "url('data:image/svg+xml;utf8,<svg viewBox=\"0 0 16 16\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z\" fill=\"%23333\"/></svg>')"
        icon_close_hover = "url('data:image/svg+xml;utf8,<svg viewBox=\"0 0 16 16\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z\" fill=\"white\"/></svg>')"
        icon_float = "url('data:image/svg+xml;utf8,<svg viewBox=\"0 0 16 16\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M3 3h8v8H3z\" fill=\"none\" stroke=\"%23333\" stroke-width=\"1.5\"/><path d=\"M13 13h-8\" stroke=\"%23333\" stroke-width=\"1.5\"/><path d=\"M13 3v10\" stroke=\"%23333\" stroke-width=\"1.5\"/></svg>')"

        self.setStyleSheet(f"""
            /* --- KHOẢNG CÁCH VÀ VIỀN NGĂN CÁCH (Handle Gap) --- */
            QMainWindow::separator {{
                background-color: #F0F0F0;
                width: 6px; /* Độ rộng để chuột có thể nắm kéo */
                
                /* Tạo viền trái để ngăn cách với Sidebar */
                border-left: 1px solid #D3D3D3; 
                
                /* Viền phải trong suốt để liền mạch với Editor (vì Editor đã xóa viền trái) */
                border-right: none; 
                margin: 0px;
                padding: 0px;
            }}
            QMainWindow::separator:hover {{
                background-color: #E6E6E6;
            }}

            /* --- PROJECT MANAGER SIDEBAR STYLE --- */
            QDockWidget {{
                border: none;
                font-family: 'Segoe UI', sans-serif; 
                margin: 0px; 
                padding: 0px;
            }}
            
            QDockWidget::title {{
                background: #F8F9FA;
                padding-left: 10px;
                padding-top: 6px;
                padding-bottom: 6px;
                font-weight: 600;
                color: #333;
                border-bottom: 1px solid #E0E0E0;
                text-align: left;
            }}

            /* --- NÚT ĐÓNG (CLOSE) --- */
            QDockWidget::close-button {{
                border: none;
                background: transparent;
                border-radius: 4px;
                icon-size: 16px; 
                subcontrol-position: top right;
                subcontrol-origin: margin;
                right: 6px; 
                top: 0px; 
                width: 24px;  
                height: 24px;
                image: {icon_close}; 
            }}

            QDockWidget::close-button:hover {{
                background: #E81123; 
                image: {icon_close_hover};
            }}
            QDockWidget::close-button:pressed {{
                background: #BF0F1D;
            }}

            /* --- NÚT FLOAT --- */
            QDockWidget::float-button {{
                border: none;
                background: transparent;
                border-radius: 4px;
                icon-size: 16px;
                subcontrol-position: top right;
                subcontrol-origin: margin;
                right: 34px; 
                top: 0px;
                width: 24px;
                height: 24px;
                image: {icon_float};
            }}

            QDockWidget::float-button:hover {{
                background: #E0E0E0;
            }}
            QDockWidget::float-button:pressed {{
                background: #CACACA;
            }}
        """)

        central_widget = QWidget()
        # [ADD] Đảm bảo container không có nền/viền gây cấn pixel
        central_widget.setStyleSheet("background: transparent; border: none; margin: 0px; padding: 0px;")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)       
        # Đảm bảo layout chính không tạo khoảng trống thừa
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.editor_workspace = EditorWorkspace()
        main_layout.addWidget(self.editor_workspace)

    def connect_signals(self):
        self.camera_manager.frame_received_signal.connect(self.update_image)
        self.camera_manager.error_occurred_signal.connect(self.show_error)
        self.editor_workspace.sig_request_open_file.connect(self.action_open_file_in_editor)

    def connect_sidebar_signals(self):
        sb = self.sidebar
        sb.sig_new_item.connect(self.action_new_structure) 
        sb.sig_delete.connect(self.action_delete_project)
        sb.sig_rename.connect(self.action_rename_project)
        sb.sig_save.connect(self.handle_save_request)
        sb.sig_save_as.connect(self.action_save_as_project)
        
        sb.sig_import_file.connect(self.handle_open_project) 
        sb.sig_import_item.connect(self.handle_open_item)    
        
        sb.sig_paste_to_project.connect(self.action_paste_item)
        sb.sig_item_delete.connect(self.action_delete_item)
        sb.sig_item_rename.connect(self.action_rename_item)
        sb.sig_item_copy.connect(self.action_copy_item)
        sb.sig_item_cut.connect(self.action_cut_item)
        sb.sig_item_save.connect(self.action_save_item)
        sb.sig_open_editor.connect(self.action_open_file_in_editor)

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    # --- LOGIC HANDLERS ---
    
    def handle_delete_from_menu(self):
        if not hasattr(self.sidebar, 'get_current_selection_info'):
            return

        result = self.sidebar.get_current_selection_info()
        if not result or all(v is None for v in result):
            QMessageBox.information(self, "Selection", "Please select a Project or Item in the sidebar to delete.")
            return

        proj_name, item_name, selection_type = result
        
        if selection_type == 'PROJECT':
            self.action_delete_project(proj_name)
        elif selection_type == 'ITEM':
            self.action_delete_item(proj_name, item_name)
        else:
            QMessageBox.information(self, "Selection", "Please select a Project or Item to delete.")

    def handle_close_editor(self):
        success = self.editor_workspace.close_current_tab()
        if not success:
            self.system_status_bar.showMessage("No active editor to close.")

    def handle_close_all_editors(self):
        self.editor_workspace.close_all_tabs()
        self.system_status_bar.showMessage("All editors closed.")

    def action_copy_item(self, project_name, folder_name):
        self.clipboard_data = {'project': project_name, 'folder': folder_name, 'action': 'COPY'}
        self.system_status_bar.showMessage(f"Copied: '{folder_name}'")

    def action_cut_item(self, project_name, folder_name):
        self.clipboard_data = {'project': project_name, 'folder': folder_name, 'action': 'CUT'}
        self.system_status_bar.showMessage(f"Cut: '{folder_name}'")

    def action_save_item(self, project_name, folder_name):
        self.handle_save_request(project_name)
        self.system_status_bar.showMessage(f"Saved item '{folder_name}'")

    def action_paste_item(self, target_project_name):
        if not self.clipboard_data:
            QMessageBox.information(self, "Paste", "Clipboard is empty.")
            return
        
        src_project = self.clipboard_data['project']
        src_folder = self.clipboard_data['folder']
        action_type = self.clipboard_data.get('action', 'COPY')
        
        if action_type == 'COPY':
            success, msg, new_name = self.project_manager.copy_item_structure(
                src_project, src_folder, target_project_name
            )
            if success:
                self.sidebar.add_structure_item(target_project_name, new_name)
                self.system_status_bar.showMessage(f"Pasted '{new_name}' to '{target_project_name}'")
            else:
                QMessageBox.warning(self, "Paste Error", msg)
        
        elif action_type == 'CUT':
            success, msg, new_name = self.project_manager.move_item_structure(
                src_project, src_folder, target_project_name
            )
            if success:
                self.sidebar.add_structure_item(target_project_name, new_name)
                self.sidebar.remove_item_node(src_project, src_folder)
                self.system_status_bar.showMessage(f"Moved '{new_name}' to '{target_project_name}'")
                self.clipboard_data = None 
            else:
                QMessageBox.warning(self, "Move Error", msg)

    def action_open_file_in_editor(self, project_name, relative_path):
        full_path = self.project_manager.get_file_path(project_name, relative_path)
        if not full_path or not os.path.exists(full_path):
            QMessageBox.warning(self, "Error", "File not found.")
            return

        file_info = QFileInfo(full_path)
        if file_info.size() > 5 * 1024 * 1024: 
            QMessageBox.warning(self, "Performance Warning", 
                                f"File '{file_info.fileName()}' is too large (>5MB) to open in this editor.")
            return

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            file_name = os.path.basename(full_path)
            self.editor_workspace.add_editor_tab(project_name, file_name, content, full_path)
        except UnicodeDecodeError:
            QMessageBox.warning(self, "Read Error", "Cannot read binary or non-utf8 file.")
        except Exception as e:
            QMessageBox.warning(self, "Read Error", f"Cannot read file:\n{str(e)}")

    def handle_create_project(self):
        default_name = f"Untitled-{self.untitled_count}"
        try:
            self.project_manager.create_project(default_name, specific_path=None)
            self.sidebar.add_project_item(default_name)
            self.untitled_count += 1
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def handle_open_project(self, project_name_placeholder=None):
        folder = QFileDialog.getExistingDirectory(self, "Open Project Directory")
        if not folder: return

        if self.project_manager.is_folder_item(folder):
            QMessageBox.critical(self, "Error", "Cannot open an Item as a Project.\nUse 'Open Item...' instead.")
            return

        success, project_name, items = self.project_manager.open_project(folder)
        if success:
            self.sidebar.add_project_item(project_name)
            for item_folder in items:
                self.sidebar.add_structure_item(project_name, item_folder)
        else:
            QMessageBox.warning(self, "Open Error", project_name)

    def handle_open_item_from_menu(self):
        current_project_name = self.sidebar.get_current_project()
        if not current_project_name:
            QMessageBox.warning(self, "Selection Required", "Please select a Project in the Sidebar first.")
            return
        self.handle_open_item(current_project_name)

    def handle_open_item(self, current_project_name):
        folder = QFileDialog.getExistingDirectory(self, f"Open Item for '{current_project_name}'")
        if not folder: return

        if not self.project_manager.is_folder_item(folder):
             QMessageBox.critical(self, "Error", "Selected folder is not a valid Item.")
             return

        if not self.project_manager.verify_item_belongs_to_project(current_project_name, folder):
             QMessageBox.critical(self, "Access Denied", "Item does not belong to the selected Project.")
             return

        folder_name = os.path.basename(folder)
        self.sidebar.add_structure_item(current_project_name, folder_name)
        self.system_status_bar.showMessage(f"Opened item '{folder_name}'.")

    def action_new_structure(self, project_name):
        folder_name, ok = QInputDialog.getText(self, "New Item", f"Create new item in '{project_name}':")
        if ok and folder_name:
            success, msg_or_path = self.project_manager.create_structure(project_name, folder_name)
            if success:
                self.sidebar.add_structure_item(project_name, folder_name)
            else:
                QMessageBox.warning(self, "Error", msg_or_path)

    def action_delete_item(self, project_name, folder_name):
        is_temp = self.project_manager.is_project_temp(project_name)
        title = "Delete Resources"
        msg = f"Remove item '{folder_name}' from the project '{project_name}'?"
        
        full_path = self.project_manager.get_file_path(project_name, folder_name)

        dlg = DeleteResourcesDialog(self, title, msg, full_path, show_checkbox=(not is_temp))
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg.is_delete_disk_checked():
                success, msg = self.project_manager.delete_item(project_name, folder_name)
                if success:
                    self.sidebar.remove_item_node(project_name, folder_name)
                    self.system_status_bar.showMessage(f"Deleted '{folder_name}' permanently.")
                else:
                    QMessageBox.warning(self, "Error", msg)
            else:
                self.sidebar.remove_item_node(project_name, folder_name)
                self.system_status_bar.showMessage(f"Removed '{folder_name}' from view.")
        
        dlg.deleteLater()

    def action_rename_item(self, project_name, folder_name, new_name=None):
        if not new_name:
             new_name, ok = QInputDialog.getText(self, "Rename Item", "New Name:", text=folder_name)
             if not ok or not new_name: return

        if new_name != folder_name:
            success, msg = self.project_manager.rename_item(project_name, folder_name, new_name)
            if success:
                self.sidebar.rename_item_node(project_name, folder_name, new_name)
            else:
                QMessageBox.warning(self, "Error", msg)

    def action_save_as_project(self, project_name):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory to Save Project")
        if not folder: return
        success, msg = self.project_manager.save_project_as(project_name, folder)
        if success:
            QMessageBox.information(self, "Saved", f"Project saved to {msg}")
        else:
            QMessageBox.warning(self, "Error", msg)

    def handle_save_request(self, project_name=None):
        if not project_name: 
            project_name = self.sidebar.get_current_project()
        
        if not project_name: return

        if self.project_manager.is_project_temp(project_name):
            self.action_save_as_project(project_name)
        else:
            self.project_manager.save_project(project_name)
            self.system_status_bar.showMessage(f"Project '{project_name}' saved.")

    def action_delete_project(self, project_name):
        is_temp = self.project_manager.is_project_temp(project_name)
        title = "Delete Resources"
        msg = f"Remove project '{project_name}' from the workspace?"
        
        full_path = self.project_manager.current_projects.get(project_name, "")

        dlg = DeleteResourcesDialog(self, title, msg, full_path, show_checkbox=(not is_temp))
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg.is_delete_disk_checked():
                success, msg = self.project_manager.delete_project(project_name)
                if success:
                    self.sidebar.remove_project_item(project_name)
                    self.system_status_bar.showMessage(f"Deleted project '{project_name}' permanently.")
                else:
                    QMessageBox.warning(self, "Error", msg)
            else:
                self.project_manager.close_project(project_name)
                self.sidebar.remove_project_item(project_name)
                self.system_status_bar.showMessage(f"Removed project '{project_name}' from workspace.")
        
        dlg.deleteLater()

    def action_rename_project(self, project_name):
        new_name, ok = QInputDialog.getText(self, "Rename Project", "New Name:", text=project_name)
        if ok and new_name and new_name != project_name:
            success, msg = self.project_manager.rename_project(project_name, new_name)
            if success:
                self.sidebar.rename_project_item(project_name, new_name)

    @pyqtSlot(QImage)
    def update_image(self, qt_img): 
        pass 

    @pyqtSlot(str)
    def show_error(self, message): 
        self.system_status_bar.showMessage(f"ERROR: {message}")