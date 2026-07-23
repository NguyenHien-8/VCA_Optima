# App/Presentation/Views/Widgets/FileEditorWorkspace/MotorControlEditor.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGridLayout, QGroupBox,
                             QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal


class MotorControlEditor(QWidget):
    """
    This widget is specifically designed to handle the Motor Control interface.
    It emits signals when the user interacts with the motor.
    """
    
    move_up_requested = pyqtSignal(str, str)      # height, speed
    move_down_requested = pyqtSignal(str, str)    # height, speed
    stop_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Setting up the UI for Motor Control"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- Motor Group ---
        motor_group = QGroupBox("Motor Control")
        motor_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        motor_inner_layout = QHBoxLayout(motor_group)
        motor_inner_layout.setContentsMargins(1, 1, 1, 1)
        motor_inner_layout.setSpacing(5)
        motor_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # --- LEFT COLUMN: Input Height & Speed ---
        input_grid = QGridLayout()
        input_grid.setVerticalSpacing(50)
        input_grid.setHorizontalSpacing(10)
        
        # Height row
        lbl_h = QLabel("Height:")
        lbl_h.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.cmb_height = QComboBox()
        self.cmb_height.setEditable(True)
        self.cmb_height.addItems(["2", "5", "10", "20", "50"])
        self.cmb_height.setFixedSize(120, 28)
        lbl_unit_h = QLabel("mm")
        lbl_unit_h.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        input_grid.addWidget(lbl_h, 0, 0)
        input_grid.addWidget(self.cmb_height, 0, 1)
        input_grid.addWidget(lbl_unit_h, 0, 2)
        
        # Speed row
        lbl_s = QLabel("Speed:")
        lbl_s.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.cmb_speed = QComboBox()
        self.cmb_speed.setEditable(True)
        self.cmb_speed.addItems(["Slow", "Medium", "Fast"])
        self.cmb_speed.setFixedSize(120, 28)
        lbl_unit_s = QLabel("rpm")
        lbl_unit_s.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        input_grid.addWidget(lbl_s, 1, 0)
        input_grid.addWidget(self.cmb_speed, 1, 1)
        input_grid.addWidget(lbl_unit_s, 1, 2)
        
        input_container = QWidget()
        input_container.setLayout(input_grid)
        motor_inner_layout.addWidget(input_container, stretch=0, 
                                    alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # --- RIGHT COLUMN: Navigation buttons ---
        ctrl_layout = QVBoxLayout()
        ctrl_layout.setSpacing(8)
        ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_up = QPushButton("▲")
        self.btn_up.setObjectName("DirectionBtn")
        self.btn_up.setFixedSize(50, 50)
        self.btn_up.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_up.setToolTip("Move Up")
        
        self.btn_stop = QPushButton("⊘")
        self.btn_stop.setObjectName("StopBtn")
        self.btn_stop.setFixedSize(50, 50)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.setToolTip("Stop Motor")
        
        self.btn_down = QPushButton("▼")
        self.btn_down.setObjectName("DirectionBtn")
        self.btn_down.setFixedSize(50, 50)
        self.btn_down.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_down.setToolTip("Move Down")
        
        ctrl_layout.addWidget(self.btn_up)
        ctrl_layout.addWidget(self.btn_stop)
        ctrl_layout.addWidget(self.btn_down)
        
        ctrl_container = QWidget()
        ctrl_container.setLayout(ctrl_layout)
        motor_inner_layout.addWidget(ctrl_container, stretch=0,
                                    alignment=Qt.AlignmentFlag.AlignVCenter)
        
        layout.addWidget(motor_group)
    
    def connect_signals(self):
        """Connect button clicks to signals."""
        self.btn_up.clicked.connect(self._on_up_clicked)
        self.btn_down.clicked.connect(self._on_down_clicked)
        self.btn_stop.clicked.connect(self._on_stop_clicked)
    
    # --- Event handlers ---
    @pyqtSlot()
    def _on_up_clicked(self):
        """Handle the Up button click."""
        height = self.cmb_height.currentText()
        speed = self.cmb_speed.currentText()
        self.move_up_requested.emit(height, speed)
    
    @pyqtSlot()
    def _on_down_clicked(self):
        """Handle the Down button click."""
        height = self.cmb_height.currentText()
        speed = self.cmb_speed.currentText()
        self.move_down_requested.emit(height, speed)
    
    @pyqtSlot()
    def _on_stop_clicked(self):
        """Handle the Stop button click."""
        self.stop_requested.emit()
    
    # --- Public API for external control ---  
    def get_height(self):
        """Get the current height value"""
        return self.cmb_height.currentText()
    
    def get_speed(self):
        """Get the current speed value"""
        return self.cmb_speed.currentText()
    
    def set_height(self, value):
        """Set the height value"""
        self.cmb_height.setCurrentText(str(value))
    
    def set_speed(self, value):
        """Set the speed value"""
        self.cmb_speed.setCurrentText(str(value))