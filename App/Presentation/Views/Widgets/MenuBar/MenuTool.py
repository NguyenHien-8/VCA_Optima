# App/Presentation/Views/Widgets/MenuBar/MenuHelp.py
from PyQt6.QtWidgets import QMenu, QStyle
from PyQt6.QtGui import QAction  

class MenuTool(QMenu):
    def __init__(self, parent_window):
        super().__init__("Tools", parent_window)
        self.addAction(QAction("Settings", self, triggered=lambda: print("[Tools] Settings")))