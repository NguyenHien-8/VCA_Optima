from PyQt6.QtWidgets import QMenu, QStyle
from PyQt6.QtGui import QAction, QKeySequence

class MenuFile(QMenu):
    def __init__(self, parent_window):
        super().__init__("File", parent_window)
        self.parent_window = parent_window
        self.setup_actions()

    def setup_actions(self):
        style = self.style() # Lấy icon hệ thống

        # Helper nhỏ để tạo action nhanh gọn
        def add(text, method, icon_enum, shortcut=None):
            action = QAction(style.standardIcon(icon_enum), text, self)
            if shortcut: action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(method)
            self.addAction(action)

        add("New Project...", self.on_new, QStyle.StandardPixmap.SP_FileIcon, "Ctrl+N")
        add("Open", self.on_open, QStyle.StandardPixmap.SP_DirOpenIcon, "Ctrl+O")
        
        self.addSeparator()
        
        add("Import", self.on_import, QStyle.StandardPixmap.SP_ArrowRight)
        add("Export", self.on_export, QStyle.StandardPixmap.SP_ArrowLeft)
        
        self.addSeparator()
        
        add("Save", self.on_save, QStyle.StandardPixmap.SP_DialogSaveButton, "Ctrl+S")
        
        self.addSeparator()
        
        add("Exit", self.on_exit, QStyle.StandardPixmap.SP_DialogCloseButton)

    # --- LOGIC ---
    def on_new(self): print("[File] New Project")
    def on_open(self): print("[File] Open Project")
    def on_import(self): print("[File] Import")
    def on_export(self): print("[File] Export")
    def on_save(self): print("[File] Save")
    def on_exit(self): 
        if self.parent_window: self.parent_window.close()