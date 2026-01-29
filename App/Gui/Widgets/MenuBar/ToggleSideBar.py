from PyQt6.QtWidgets import (QDockWidget, QTabWidget, QWidget, QVBoxLayout, 
                             QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog, QMessageBox) 
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QAction 
from PyQt6.QtCore import Qt, pyqtSignal

class ProjectSidebar(QDockWidget):
    # Signals
    sig_new_file = pyqtSignal(str)      # Gửi tên project
    sig_copy = pyqtSignal(str)
    sig_delete = pyqtSignal(str)
    sig_rename = pyqtSignal(str)
    sig_save = pyqtSignal(str)
    sig_save_as = pyqtSignal(str)       # [NEW] Save As Signal
    sig_close_proj = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__("Project Manager", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.setMinimumWidth(150)
        self.setMaximumWidth(800)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        self.tab_project = QWidget()
        self.setup_tab_project()
        self.tabs.addTab(self.tab_project, "Project")
        
        self.tab_calibration = QWidget()
        self.setup_tab_calibration() 
        self.tabs.addTab(self.tab_calibration, "Calibration Tool")
        
        layout.addWidget(self.tabs)
        self.setWidget(container)

    def setup_tab_project(self):
        layout = QVBoxLayout(self.tab_project)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # [CHANGE] Dùng QTreeWidget thay vì QListWidget để hiển thị Project -> File
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderHidden(True) # Ẩn tiêu đề cột
        self.project_tree.setStyleSheet("border: 1px solid #C0C0C0;")
        
        # Context Menu
        self.project_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.project_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.project_tree)

    def setup_tab_calibration(self):
        layout = QVBoxLayout(self.tab_calibration)
        layout.setContentsMargins(0, 0, 0, 0)
        # Tab này giữ nguyên logic cũ hoặc update sau
        self.calibration_list = QTreeWidget() 
        self.calibration_list.setHeaderHidden(True)
        self.calibration_list.setStyleSheet("border: 1px solid #C0C0C0;")
        layout.addWidget(self.calibration_list)

    def show_context_menu(self, pos):
        item = self.project_tree.itemAt(pos)
        if item is None:
            return 
        
        # Logic: Item cha (Project) hay Item con (File)?
        # Ở đây giả định user click vào Project để tạo file/save as
        # Nếu item không có parent -> Là Project
        if item.parent() is None:
            project_name = item.text(0)
            self._show_project_context_menu(project_name, pos)
        else:
            # Nếu click vào File -> Có thể thêm logic Edit/Delete file sau này
            pass

    def _show_project_context_menu(self, project_name, pos):
        menu = QMenu(self)

        act_new_file = menu.addAction("New File")
        menu.addSeparator()
        act_rename = menu.addAction("Rename Project")
        act_delete = menu.addAction("Delete Project")
        menu.addSeparator()
        act_save = menu.addAction("Save")
        act_save_as = menu.addAction("Save As...") # [NEW]
        menu.addSeparator()
        act_close = menu.addAction("Close Project")

        action = menu.exec(self.project_tree.mapToGlobal(pos))

        if action == act_new_file: self.sig_new_file.emit(project_name)
        elif action == act_delete: self.sig_delete.emit(project_name)
        elif action == act_rename: self.sig_rename.emit(project_name)
        elif action == act_save: self.sig_save.emit(project_name)
        elif action == act_save_as: self.sig_save_as.emit(project_name)
        elif action == act_close: self.sig_close_proj.emit(project_name)

    # --- PUBLIC METHODS FOR MAINWINDOW ---

    def add_project_item(self, project_name):
        # Kiểm tra trùng
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if not items:
            item = QTreeWidgetItem(self.project_tree)
            item.setText(0, project_name)
            item.setIcon(0, QIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon)))
            self.project_tree.addTopLevelItem(item)
            item.setExpanded(True) # Mở rộng folder luôn
            self.project_tree.setCurrentItem(item)

    def add_file_item(self, project_name, file_name):
        # [NEW] Thêm file vào dưới project
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if items:
            project_item = items[0]
            file_item = QTreeWidgetItem(project_item)
            file_item.setText(0, file_name)
            file_item.setIcon(0, QIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon)))
            project_item.setExpanded(True)

    def remove_project_item(self, project_name):
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        for item in items:
            index = self.project_tree.indexOfTopLevelItem(item)
            self.project_tree.takeTopLevelItem(index)
    
    def rename_project_item(self, old_name, new_name):
        items = self.project_tree.findItems(old_name, Qt.MatchFlag.MatchExactly)
        if items:
            items[0].setText(0, new_name)

    def get_current_project(self):
        item = self.project_tree.currentItem()
        if item:
            # Nếu chọn file con, trả về cha (Project)
            if item.parent():
                return item.parent().text(0)
            return item.text(0)
        return None

# Class ToggleAction giữ nguyên
class ToggleAction(QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Toggle Sidebar")
        self.setIcon(self.create_sidebar_icon())

    def create_sidebar_icon(self):
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(Qt.GlobalColor.black)
        painter.drawRect(2, 4, 20, 16)
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawRect(2, 4, 6, 16) 
        painter.end()
        return QIcon(pixmap)