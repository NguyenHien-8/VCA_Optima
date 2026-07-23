# App/Presentation/Views/Widgets/StatusBar.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame

class StatusIndicator(QWidget):
    """The child widget displays each status item (circle icon + text)"""
    def __init__(self, label_text="Unknown", default_color="#7f8c8d"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setSpacing(5)

        self.lbl_dot = QLabel()
        self.lbl_dot.setFixedSize(12, 12)
        self.lbl_dot.setStyleSheet(f"background-color: {default_color}; border-radius: 6px;")
        self.lbl_text = QLabel(label_text)
        self.lbl_text.setStyleSheet("font-weight: bold; color: #333;")

        layout.addWidget(self.lbl_dot)
        layout.addWidget(self.lbl_text)
    
    def set_status(self, text, color_hex):
        self.lbl_text.setText(text)
        self.lbl_dot.setStyleSheet(f"background-color: {color_hex}; border-radius: 6px;")

class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(20)
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1; 
                border-top: 1px solid #bdc3c7;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(15)

        # Label Notification 
        self.lbl_message = QLabel("")
        self.lbl_message.setStyleSheet("color: #2c3e50; border: none;")
        layout.addWidget(self.lbl_message)
        layout.addStretch()

        # Separator line
        self._add_separator(layout)

        # CAMERA STATUS
        self.camera_status = StatusIndicator("Cam: Disconnected", "#e74c3c")  # Red
        layout.addWidget(self.camera_status)

        self._add_separator(layout)

        # HARDWARE PORT STATUS
        self.hardware_status = StatusIndicator("Port: None", "#e74c3c")  # Red
        layout.addWidget(self.hardware_status)

    def _add_separator(self, layout):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #bdc3c7; border: none; background-color: #bdc3c7; width: 1px;")
        line.setFixedWidth(1)
        layout.addWidget(line)

    # --- METHODS TO UPDATE STATUS ---
    def show_message(self, msg):
        self.lbl_message.setText(msg)

    def set_hardware_connected(self, is_connected, port_name=""):
        if is_connected:
            self.hardware_status.set_status(f"Port: {port_name}", "#2ecc71")  # Green
        else:
            self.hardware_status.set_status("Port: Disconnected", "#e74c3c")  # Red

    def set_camera_connected(self, is_connected, cam_name=""):
        if is_connected:
            self.camera_status.set_status(f"Cam: {cam_name}", "#2ecc71")  # Green
        else:
            self.camera_status.set_status("Cam: Disconnected", "#e74c3c")  # Red