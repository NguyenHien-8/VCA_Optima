###############################################################################
# @file App/Presentation/ViewModels/DialogViewModel/ConfigHardwareViewModel.py
# Author: TRAN NGUYEN HIEN
# Email: trannguyenhien29085@gmail.com
###############################################################################
from PyQt6.QtCore import QObject
from App.Models.CamHardwareManager import HardwareConfigBackend

class ConfigHardwareViewModel(QObject):
    def __init__(self, hardware_manager):
        super().__init__()
        self.backend = HardwareConfigBackend(hardware_manager)

    def get_current_config(self):
        return self.backend.get_current_config()

    def scan_ports(self):
        return self.backend.scan_ports()

    def apply_connection(self, port, baud, period):
        return self.backend.apply_connection(port, baud, period)