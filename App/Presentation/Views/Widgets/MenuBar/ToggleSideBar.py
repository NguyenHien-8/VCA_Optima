###############################################################
# @file App/Presentation/Views/Widgets/MenuBar/ToggleSideBar.py
# Author: TRAN NGUYEN HIEN
# Email: trannguyenhien29085@gmail.com
###############################################################
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt

class ToggleAction(QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Toggle Sidebar")
        self._cached_icon = self.create_sidebar_icon()
        self.setIcon(self._cached_icon)

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