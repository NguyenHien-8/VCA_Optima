from PyQt6.QtWidgets import QMenu, QStyle
from PyQt6.QtGui import QAction

class MenuControl(QMenu):
    def __init__(self, parent_window):
        super().__init__("Control", parent_window)
        self.parent_window = parent_window
        self.setup_actions()

    def setup_actions(self):
        style = self.style()

        # Pump Fluid
        act_pump = QAction(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay), "Pump Fluid", self)
        act_pump.triggered.connect(self.on_pump)
        self.addAction(act_pump)

        # Stop Pump
        act_stop = QAction(style.standardIcon(QStyle.StandardPixmap.SP_MediaStop), "Stop Pump", self)
        act_stop.triggered.connect(self.on_stop)
        self.addAction(act_stop)

        # Move Stage
        act_move = QAction(style.standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward), "Move Stage", self)
        act_move.triggered.connect(self.on_move)
        self.addAction(act_move)

    def on_pump(self): print("[Control] Pump Start")
    def on_stop(self): print("[Control] Pump Stop")
    def on_move(self): print("[Control] Move Stage")