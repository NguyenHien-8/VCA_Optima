# App/Presentation/ViewModels/DialogViewModel/MotorControlViewModel.py
from PyQt6.QtCore import QObject, pyqtSignal

class MotorControlViewModel(QObject):
    motor_state_changed = pyqtSignal(bool, bool)

    def __init__(self, control_manager):
        super().__init__()
        self.control_manager = control_manager

    def move_up(self, height, speed):
        self.motor_state_changed.emit(True, True)
        success, msg = self.control_manager.request_move_up(height, speed)
        self.motor_state_changed.emit(False, True)
        return success, msg

    def move_down(self, height, speed):
        self.motor_state_changed.emit(True, False)
        success, msg = self.control_manager.request_move_down(height, speed)
        self.motor_state_changed.emit(False, False)
        return success, msg

    def stop(self):
        success, msg = self.control_manager.request_stop()
        return success, msg