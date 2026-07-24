############################################################
# @file App/Presentation/Views/Widgets/MenuBar/MenuFile.py
# Author: TRAN NGUYEN HIEN
# Email: trannguyenhien29085@gmail.com
############################################################
import os
import sys
from PyQt6.QtWidgets import QMenu, QApplication
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from PyQt6.QtCore import QProcess

from .KeyboardShortcut import *
from App.Infrastructure.Helpers.ResourceHelper import resource_path

class MenuFile(QMenu):
    def __init__(self, parent_window):
        super().__init__("File", parent_window)
        self.parent_window = parent_window 
        self.setup_actions()
        self._add_rename_shortcut()

    def setup_actions(self):
        icon_base_path = resource_path(os.path.join("App", "ReSource", "Icon", "MenuFile"))

        def get_icon(filename):
            path = os.path.join(icon_base_path, filename)
            if os.path.exists(path):
                return QIcon(path)
            return QIcon()

        def add(text, method, icon_filename, shortcut=None, target_menu=None):
            icon = get_icon(icon_filename)
            action = QAction(icon, text, self)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(method)
            if target_menu:
                target_menu.addAction(action)
            else:
                self.addAction(action)

        # --- GROUP: NEW ---
        new_submenu = QMenu("New", self)
        new_submenu.setIcon(get_icon("new.svg"))
        self.addMenu(new_submenu)
        add("New Project...", self.on_new_project, "new_project.svg",
            SHORTCUT_NEW_PROJECT, target_menu=new_submenu)
        add("New Item...", self.on_new_item, "new_item.svg",
            SHORTCUT_NEW_ITEM, target_menu=new_submenu)

        self.addSeparator()

        # --- GROUP: OPEN ---
        add("Open Project...", self.on_open_project, "open_project.svg",
            SHORTCUT_OPEN_PROJECT)
        add("Open Item...", self.on_open_item, "open_item.svg",
            SHORTCUT_OPEN_ITEM)

        self.addSeparator()

        # --- GROUP: SAVE ---
        # add("Save", self.on_save, "save.svg", SHORTCUT_SAVE)
        add("Save As...", self.on_save_as, "save.svg", SHORTCUT_SAVE_AS)
        # add("Save All", self.on_save_all, "save.svg", SHORTCUT_SAVE_ALL)

        self.addSeparator()

        # --- GROUP: DELETE ---
        add("Delete", self.on_delete, "delete.svg", SHORTCUT_DELETE)

        self.addSeparator()

        # --- GROUP: RESTART / EXIT ---
        add("Restart", self.on_restart, "restart.svg", SHORTCUT_RESTART)
        add("Exit", self.on_exit, "exit.svg", SHORTCUT_EXIT)

    def _add_rename_shortcut(self):
        """Added Ctrl+R shortcut for Rename (hidden action, not visible in the menu)."""
        self.action_rename = QAction("Rename", self)
        self.action_rename.setShortcut(QKeySequence(SHORTCUT_RENAME))
        self.action_rename.triggered.connect(self.on_rename)
        self.parent_window.addAction(self.action_rename)

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

    # def on_save(self):
    #     if hasattr(self.parent_window, "save_project"):
    #         self.parent_window.save_project()
    #     else:
    #         print("Warning: MainWindow has no 'save_project' method")

    def on_save_as(self):
        if hasattr(self.parent_window, "save_as_project"):
            self.parent_window.save_as_project()
        else:
            print("Warning: MainWindow has no 'save_as_project' method")

    # def on_save_all(self):
    #     print("[File] Save All - Not implemented yet")

    def on_delete(self):
        if hasattr(self.parent_window, "delete_selected"):
            self.parent_window.delete_selected()
        else:
            print("Warning: MainWindow has no 'delete_selected' method")

    def on_restart(self):
        """Restart the application (Ctrl+Alt+R)"""
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)

    def on_exit(self):
        QApplication.quit()

    def on_rename(self):
        """Call rename_selected in MainView (Ctrl+R)"""
        if hasattr(self.parent_window, "rename_selected"):
            self.parent_window.rename_selected()
        else:
            print("Warning: MainWindow has no 'rename_selected' method")