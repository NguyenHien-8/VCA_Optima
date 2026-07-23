# App/Presentation/Views/Widgets/MenuBar/MenuFile.py
import sys
from PyQt6.QtWidgets import QMenu, QStyle, QApplication
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import QProcess

class MenuFile(QMenu):
    def __init__(self, parent_window):
        super().__init__("File", parent_window)
        self.parent_window = parent_window 
        self.setup_actions()

    def setup_actions(self):
        style = self.style()
        def add(text, method, icon_enum, shortcut=None):
            action = QAction(style.standardIcon(icon_enum), text, self)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(method)
            self.addAction(action)

        # --- GROUP: NEW ---
        new_submenu = QMenu("New", self)
        new_submenu.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        
        act_new_project = QAction("New Project...", self)
        act_new_project.setShortcut(QKeySequence("Alt+Shift+N"))
        act_new_project.triggered.connect(self.on_new_project)
        new_submenu.addAction(act_new_project)

        act_new_item = QAction("New Item...", self)
        act_new_item.setShortcut(QKeySequence("Ctrl+N"))
        act_new_item.triggered.connect(self.on_new_item)
        new_submenu.addAction(act_new_item)
        
        self.addMenu(new_submenu)
        self.addSeparator()

        # --- GROUP: OPEN ---
        act_open_proj = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DirIcon), "Open Project...", self)
        act_open_proj.setShortcut(QKeySequence("Ctrl+O"))
        act_open_proj.triggered.connect(self.on_open_project)
        self.addAction(act_open_proj)

        act_open_item = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon), "Open Item...", self)
        act_open_item.setShortcut(QKeySequence("Ctrl+Shift+O"))
        act_open_item.triggered.connect(self.on_open_item)
        self.addAction(act_open_item)
        
        self.addSeparator()

        # --- GROUP: SAVE ---
        add("Save", self.on_save, QStyle.StandardPixmap.SP_DialogSaveButton, "Ctrl+S")
        add("Save As...", self.on_save_as, QStyle.StandardPixmap.SP_DialogSaveButton, "Ctrl+Shift+S")
        add("Save All", self.on_save_all, QStyle.StandardPixmap.SP_DialogSaveButton, "Ctrl+Alt+S")
        
        self.addSeparator()

        # --- GROUP: DELETE ---
        add("Delete", self.on_delete, QStyle.StandardPixmap.SP_TrashIcon, "Del")

        self.addSeparator()
        
        # --- GROUP: CLOSE EDITOR ---
        add("Close Editor", self.on_close_editor, QStyle.StandardPixmap.SP_DialogCloseButton, "Ctrl+W")
        add("Close All Editors", self.on_close_all_editors, QStyle.StandardPixmap.SP_DialogCloseButton, "Ctrl+Shift+W")
        
        self.addSeparator()
        act_restart = QAction(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "Restart", self)
        act_restart.triggered.connect(self.restart_app)
        self.addAction(act_restart)

        act_exit = QAction(style.standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton), "Exit", self)
        act_exit.setShortcut(QKeySequence("Alt+F4"))
        act_exit.triggered.connect(self.parent_window.close)
        self.addAction(act_exit)

    # --- ACTION HANDLERS ---
    def on_new_project(self):
        if hasattr(self.parent_window, "new_project"):
            self.parent_window.new_project()
        else:
            print("Warning: MainWindow has no 'new_project' method")

    def on_new_item(self):
        if hasattr(self.parent_window, "new_item"):
            self.parent_window.new_item()
        else:
            print("Warning: MainWindow has no 'new_item' method")

    def on_open_project(self):
        if hasattr(self.parent_window, "open_project"):
            self.parent_window.open_project()
        else:
            print("Warning: MainWindow has no 'open_project' method")

    def on_open_item(self):
        if hasattr(self.parent_window, "open_item"):
            self.parent_window.open_item()
        else:
            print("Warning: MainWindow has no 'open_item' method")

    def on_save(self):
        if hasattr(self.parent_window, "save_project"):
            self.parent_window.save_project()
        else:
            print("Warning: MainWindow has no 'save_project' method")

    def on_save_as(self):
        if hasattr(self.parent_window, "save_as_project"):
            self.parent_window.save_as_project()
        else:
            print("Warning: MainWindow has no 'save_as_project' method")

    def on_save_all(self):
        print("[File] Save All - Not implemented yet")

    def on_delete(self):
        if hasattr(self.parent_window, "delete_selected"):
            self.parent_window.delete_selected()
        else:
            print("Warning: MainWindow has no 'delete_selected' method")

    def on_close_editor(self):
        if hasattr(self.parent_window, "close_current_editor"):
            self.parent_window.close_current_editor()
        else:
            print("Warning: MainWindow has no 'close_current_editor' method")

    def on_close_all_editors(self):
        if hasattr(self.parent_window, "close_all_editors"):
            self.parent_window.close_all_editors()
        else:
            print("Warning: MainWindow has no 'close_all_editors' method")

    def restart_app(self):
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)