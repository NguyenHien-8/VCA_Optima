############################################################
# @file App/Presentation/Views/Widgets/MenuBar/MenuHelp.py
# Author: TRAN NGUYEN HIEN
# Email: trannguyenhien29085@gmail.com
############################################################
from PyQt6.QtWidgets import QMenu, QStyle
from PyQt6.QtGui import QAction  

class MenuHelp(QMenu):
    def __init__(self, parent_window):
        super().__init__("Help", parent_window)
        self.addAction(QAction("About", self, triggered=lambda: print("[Help] About")))