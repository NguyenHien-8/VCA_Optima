############################################################
# @file App/Presentation/Views/Widgets/MenuBar/MenuWindow.py
# Author: TRAN NGUYEN HIEN
# Email: trannguyenhien29085@gmail.com
############################################################
from PyQt6.QtWidgets import QMenu, QStyle
from PyQt6.QtGui import QAction 

class MenuWindow(QMenu):
    def __init__(self, parent_window):
        super().__init__("Window", parent_window)
        self.addAction(QAction("Settings", self, triggered=lambda: print("[Window] Settings")))