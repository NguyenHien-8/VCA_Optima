# App/Presentation/Views/Widgets/EditorWorkspace.py
import os
from PyQt6.QtWidgets import (QTabWidget, QWidget, QLabel, QStackedLayout, QTabBar)
from PyQt6.QtCore import pyqtSignal, Qt, QMimeData

from App.Infrastructure.Helpers.ResourceHelper import apply_stylesheet

class EditorTabBar(QTabBar):
    """
    Custom TabBar for smoother tab drag-and-drop functionality (Live Reordering).
    Ensures the Close button moves seamlessly with the tab instead of lagging behind.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False) 
        self._drag_start_pos = None
        self._drag_index = -1

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()
            self._drag_index = self.tabAt(event.pos())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # If you are holding down the left mouse button and have identified the tab you want to drag
        if self._drag_start_pos and self._drag_index != -1:
            drag_distance = (event.pos() - self._drag_start_pos).manhattanLength()         
            if drag_distance > 10: # The threshold for starting to pull
                target_index = self.tabAt(event.pos())
                
                # If the mouse moves to the area of ​​another tab
                if target_index != -1 and target_index != self._drag_index:
                    self.moveTab(self._drag_index, target_index)
                    self._drag_index = target_index
        
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None
        self._drag_index = -1
        super().mouseReleaseEvent(event)

class EditorTabWidget(QTabWidget):
    """
    Custom TabWidget use EditorTabBar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(EditorTabBar(self))

# --- END CUSTOM CLASSES ---
class EditorWorkspace(QWidget):
    """
    The class manages the main workspace.
    """
    sig_request_open_file = pyqtSignal(str, str) 
    sig_request_save_file = pyqtSignal(str, str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        # --- LAYOUT SETUP ---
        self.layout_stack = QStackedLayout(self)
        self.layout_stack.setContentsMargins(0, 0, 0, 0)
        self.layout_stack.setSpacing(0)
        
        self.placeholder_label = QLabel("") 
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setObjectName("PlaceholderLabel")
        
        self.tab_widget = EditorTabWidget()
        self.tab_widget.setTabsClosable(True) 
        self.tab_widget.setObjectName("EditorTabWidget")

        self.layout_stack.addWidget(self.placeholder_label)
        self.layout_stack.addWidget(self.tab_widget)
        self.layout_stack.setCurrentIndex(0)

        self.load_editor_workspace_style()

    def load_editor_workspace_style(self):
        apply_stylesheet(self, "EditorWorkspaceStyles.qss")

    # --- DRAG & DROP EVENTS ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            data = event.mimeData().text()
            if "|" in data:
                event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData().text()
        if "|" in data:
            project_name, file_name = data.split("|")
            self.sig_request_open_file.emit(project_name, file_name)
            event.acceptProposedAction()

    # --- TAB MANAGEMENT ---
    def add_editor_tab(self, widget, file_name, project_name, full_path):
        """
        Add tabs with custom widgets.
        Widget: QWidget displays file contents.
        """
        tab_id = self.find_tab_by_path(full_path)
        if tab_id >= 0:
            self.tab_widget.setCurrentIndex(tab_id)
            self.layout_stack.setCurrentIndex(1)
            return

        # Assign properties for management
        widget.setProperty("full_path", full_path)
        widget.setProperty("file_name", file_name)
        widget.setProperty("project_name", project_name)

        self.tab_widget.addTab(widget, file_name)
        self.tab_widget.setCurrentWidget(widget)
        self.tab_widget.setTabToolTip(self.tab_widget.currentIndex(), full_path)

        self.layout_stack.setCurrentIndex(1)

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if widget:
            if not widget.close():
                return False
            widget.deleteLater()
        self.tab_widget.removeTab(index)
        
        if self.tab_widget.count() == 0:
            self.layout_stack.setCurrentIndex(0)
        return True

    def find_tab_by_path(self, full_path):
        if full_path is None:
            return -1
        norm_path = os.path.normpath(full_path)
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            widget_path = widget.property("full_path")
            if widget_path is not None and os.path.normpath(widget_path) == norm_path:
                return i
        return -1

    def close_current_tab(self):
        current_idx = self.tab_widget.currentIndex()
        if current_idx != -1:
            self.close_tab(current_idx)
            return True
        return False

    def activate_tab_by_path(self, full_path):
        """Activate the tab if it already exists, returning True if successful."""
        idx = self.find_tab_by_path(full_path)
        if idx >= 0:
            self.tab_widget.setCurrentIndex(idx)
            self.layout_stack.setCurrentIndex(1)
            return True
        return False
