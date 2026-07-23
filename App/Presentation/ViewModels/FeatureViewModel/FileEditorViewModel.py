# App/Presentation/ViewModels/FileEditorViewModel.py
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QImage

from App.Models.MediaUtils.MediaManager import MediaManager


class FileEditorViewModel(QObject):
    frame_received = pyqtSignal(QImage)               # Camera frame
    video_state_changed = pyqtSignal(str)             # 'idle', 'recording', 'paused'
    recording_time_updated = pyqtSignal(str)          # recorded time (HH:MM:SS)
    error_occurred = pyqtSignal(str)
    motor_moving = pyqtSignal(bool)
    storage_target_changed = pyqtSignal(str, str, str)  # project_name, item_name, item_path

    def __init__(self, project_name, file_name, content, full_path,
                 camera_manager, control_panel_manager):
        super().__init__()

        self.project_name = project_name
        self.file_name = file_name
        self.content = content
        self.full_path = full_path

        self.camera_manager = camera_manager
        self.control_panel_manager = control_panel_manager

        import os
        self.item_name = os.path.basename(os.path.dirname(full_path))
        item_path = os.path.dirname(full_path)
        self.media_manager = MediaManager(item_path)

        self.recording_timer = QTimer()
        self.recording_timer.setInterval(1000)
        self.recording_timer.timeout.connect(self._on_recording_timer_timeout)
        self.elapsed_seconds = 0

    def _on_recording_timer_timeout(self):
        self.elapsed_seconds += 1
        time_str = self._format_time(self.elapsed_seconds)
        self.recording_time_updated.emit(time_str)

    def _format_time(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def receive_frame(self, qimage: QImage):
        if qimage is None or qimage.isNull():
            return
        self.frame_received.emit(qimage)
        if self.media_manager.is_recording():
            self.media_manager.update_video_frame(qimage)

    # =========================
    # STORAGE TARGET MANAGEMENT
    # =========================
    def set_storage_target(self, project_name, item_name, item_path):
        """
        Update where captured images/videos are stored.
        Safe update rule:
        - If currently recording, do not switch target.
        - If target is unchanged, do nothing.
        """
        import os

        if not item_path or not os.path.isdir(item_path):
            self.error_occurred.emit("Invalid item path for FileEditor storage.")
            return False

        current_item_path = os.path.dirname(self.full_path) if self.full_path else ""
        if os.path.normpath(current_item_path) == os.path.normpath(item_path):
            return True

        if self.media_manager.is_recording():
            self.error_occurred.emit("Cannot change save target while recording video.")
            return False

        try:
            self.media_manager.close()
        except Exception:
            pass

        self.project_name = project_name
        self.item_name = item_name
        self.file_name = f"{item_name}.session"
        self.full_path = os.path.join(item_path, self.file_name)
        self.media_manager = MediaManager(item_path)
        self.storage_target_changed.emit(project_name, item_name, item_path)
        return True

    # --- Motor Control ---
    def move_up(self, height, speed):
        self.motor_moving.emit(True)
        success, msg = self.control_panel_manager.request_move_up(height, speed)
        if not success:
            self.error_occurred.emit(msg)
        self.motor_moving.emit(False)

    def move_down(self, height, speed):
        self.motor_moving.emit(True)
        success, msg = self.control_panel_manager.request_move_down(height, speed)
        if not success:
            self.error_occurred.emit(msg)
        self.motor_moving.emit(False)

    def stop_motor(self):
        success, msg = self.control_panel_manager.request_stop()
        if not success:
            self.error_occurred.emit(msg)

    # --- Image Capture ---
    def capture_image(self, qimage):
        success, filename, message = self.media_manager.capture_image(qimage)
        if not success:
            self.error_occurred.emit(message)

    # --- Video Recording ---
    def start_video(self):
        fps = self.camera_manager.get_fps()
        if fps <= 0:
            fps = 30.0
        success, filename, message = self.media_manager.start_video(fps=fps)
        if success:
            self.elapsed_seconds = 0
            self.recording_time_updated.emit("00:00:00")
            self.recording_timer.start()
            self.video_state_changed.emit('recording')
        else:
            self.error_occurred.emit(message)

    def pause_video(self):
        if self.media_manager.pause_video():
            self.recording_timer.stop()
            self.video_state_changed.emit('paused')
        else:
            self.error_occurred.emit("Cannot pause: not recording")

    def resume_video(self):
        if self.media_manager.resume_video():
            self.recording_timer.start()
            self.video_state_changed.emit('recording')
        else:
            self.error_occurred.emit("Cannot resume: not paused")

    def stop_video(self):
        if self.media_manager.is_recording():
            success, filename, message = self.media_manager.stop_video()
            self.recording_timer.stop()
            self.elapsed_seconds = 0
            self.recording_time_updated.emit("00:00:00")
            self.video_state_changed.emit('idle')
        else:
            self.recording_timer.stop()
            self.elapsed_seconds = 0
            self.recording_time_updated.emit("00:00:00")
            self.video_state_changed.emit('idle')

    def close(self):
        if self.media_manager.is_recording():
            self.media_manager.stop_video()
        self.recording_timer.stop()
        self.media_manager.close()