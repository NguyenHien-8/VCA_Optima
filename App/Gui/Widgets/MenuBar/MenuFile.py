import sys
from PyQt6.QtWidgets import QMenu, QStyle, QApplication
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import QProcess

class MenuFile(QMenu):
    def __init__(self, parent_window):
        super().__init__("File", parent_window)
        self.parent_window = parent_window # parent_window chính là MainWindow
        self.setup_actions()

    def setup_actions(self):
        style = self.style()
        
        # Helper function
        def add(text, method, icon_enum, shortcut=None):
            action = QAction(style.standardIcon(icon_enum), text, self)
            if shortcut: action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(method)
            self.addAction(action)

        # --- GROUP: NEW ---
        new_submenu = QMenu("New", self)
        new_submenu.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon))

        act_new_project = QAction("New Project...", self)
        act_new_project.setShortcut(QKeySequence("Alt+Shift+N"))
        act_new_project.triggered.connect(self.on_new_project) # Kết nối vào logic mới
        new_submenu.addAction(act_new_project)

        act_new_file = QAction("New File...", self)
        act_new_file.setShortcut(QKeySequence("Ctrl+N"))
        act_new_file.triggered.connect(self.on_new_file)
        new_submenu.addAction(act_new_file)

        self.addMenu(new_submenu)
        self.addSeparator()

        # --- Các Group khác (Open, Save, etc.) giữ nguyên như cũ ---
        add("Open File...", self.on_open_file, QStyle.StandardPixmap.SP_DirOpenIcon)
        add("Open Project...", self.on_open_project, QStyle.StandardPixmap.SP_DirOpenIcon)
        self.addSeparator()
        add("Save", self.on_save, QStyle.StandardPixmap.SP_DialogSaveButton, "Ctrl+S")
        add("Save As...", self.on_save_as, QStyle.StandardPixmap.SP_DialogSaveButton, "Ctrl+Alt+S")
        add("Save All", self.on_save_all, QStyle.StandardPixmap.SP_DialogSaveButton, "Ctrl+Shift+S")
        self.addSeparator()
        add("Close", self.on_close, QStyle.StandardPixmap.SP_DialogCloseButton, "Ctrl+W")
        add("Close All", self.on_close_all, QStyle.StandardPixmap.SP_DialogCloseButton, "Ctrl+Shift+W")
        self.addSeparator()
        add("Import...", self.on_import, QStyle.StandardPixmap.SP_ArrowRight)
        add("Export...", self.on_export, QStyle.StandardPixmap.SP_ArrowLeft)
        self.addSeparator()
        add("Restart", self.on_restart, QStyle.StandardPixmap.SP_BrowserReload)
        add("Exit", self.on_exit, QStyle.StandardPixmap.SP_DialogCancelButton)

    # --- LOGIC (SLOTS) ---

    def on_new_project(self):
        # [UPDATED] Gọi hàm xử lý bên MainWindow
        if hasattr(self.parent_window, "handle_create_project"):
            self.parent_window.handle_create_project()
        else:
            print("Chưa implement handle_create_project ở MainWindow")

    def on_new_file(self):
        # [UPDATED] Gọi hàm xử lý bên MainWindow (tạo file cho project đang chọn)
        if hasattr(self.parent_window, "handle_create_file_in_active_project"):
            self.parent_window.handle_create_file_in_active_project()

    # Các hàm cũ giữ nguyên
    def on_open_file(self): print("[File] Open File")
    def on_open_project(self): print("[File] Open Project")
    def on_save(self): print("[File] Save")
    def on_save_as(self): print("[File] Save As")
    def on_save_all(self): print("[File] Save All")
    def on_close(self): print("[File] Close Current Tab/File")
    def on_close_all(self): print("[File] Close All Files")
    def on_import(self): print("[File] Import Project")
    def on_export(self): print("[File] Export Project")

    def on_restart(self):
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)

    def on_exit(self):
        if self.parent_window:
            self.parent_window.close()