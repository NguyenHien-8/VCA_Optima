# App/Models/Controllers/HardwareManager.py
from PyQt6.QtCore import QObject, pyqtSignal
from App.Models.Controllers.HardwareConnector import HardwareConnector

class HardwareManager(QObject):
    connection_status_changed = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.connector = HardwareConnector()
        self.current_config = {
            "port": "",
            "baud": 115200,
            "query_period": 100
        }

    def scan_ports(self):
        return self.connector.get_available_ports()

    # --- Config Management ---
    def get_config(self):
        """ Return the current configuration for the Dialog to display """
        return self.current_config.copy()
    
    def save_config(self, new_config):
        """
        Save the new configuration when the user clicks 'Apply and Close'.
        This data will be used for future connections.
        """
        self.current_config = new_config

    # --- Connection Logic (Backend) ---
    def connect_hardware(self, port, baud):
        success, msg = self.connector.connect(port, baud)
        self.connection_status_changed.emit(success, msg)
        return success, msg

    def disconnect_hardware(self):
        success, msg = self.connector.disconnect()
        self.connection_status_changed.emit(False, msg)
        return success, msg

    def is_connected(self):
        return self.connector.is_connected()

    def cleanup(self):
        """Release the serial port during application shutdown."""
        return self.connector.disconnect()
    
    def send_serial_command(self, command):
        """Receive string commands and send them through the connector"""
        if self.is_connected():
            success, msg = self.connector.write_data(command)
            if success:
                print(f"[HardwareManager] {msg}")
            else:
                print(f"[HardwareManager] Error sending: {msg}")
            return success, msg
        message = "Cannot send: hardware is not connected."
        print(f"[HardwareManager] {message}")
        return False, message
