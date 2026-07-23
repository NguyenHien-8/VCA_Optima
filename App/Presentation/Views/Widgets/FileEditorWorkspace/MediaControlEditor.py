# App/Presentation/Views/Widgets/FileEditorWorkspace/MediaControlEditor.py
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QSizePolicy, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QSize
from PyQt6.QtGui import QImage, QIcon

from App.Infrastructure.Helpers.ResourceHelper import resource_path


class MediaControlEditor(QWidget):
    capture_requested = pyqtSignal(QImage)
    record_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    resume_requested = pyqtSignal()
    stop_video_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_frame = None
        self._init_icon_paths()
        self.setup_ui()
        self.connect_signals()

    def _init_icon_paths(self):
        icon_base = resource_path(os.path.join("App", "ReSource", "Icon", "Media"))
        self.icon_photo_camera = os.path.join(icon_base, 'photo_camera.svg')
        self.icon_video_camera = os.path.join(icon_base, 'video_camera.svg')
        self.icon_pause_video = os.path.join(icon_base, 'pause_video.svg')
        self.icon_play_video = os.path.join(icon_base, 'play_video.svg')
        self.icon_stop_video = os.path.join(icon_base, 'stop_video.svg')

    def _load_icon(self, icon_path):
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            print(f"Warning: Icon not found at {icon_path}")
            return QIcon()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        media_group = QGroupBox("Camera")
        media_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        media_layout = QHBoxLayout(media_group)
        media_layout.setContentsMargins(10, 10, 10, 10)
        media_layout.setSpacing(20)
        media_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Capture Image
        self.btn_capture = QPushButton()
        self.btn_capture.setObjectName("MediaBtn")
        self.btn_capture.setIcon(self._load_icon(self.icon_photo_camera))
        self.btn_capture.setIconSize(QSize(30, 30))
        self.btn_capture.setFixedSize(50, 50)
        self.btn_capture.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_capture.setToolTip("Capture Image")
        media_layout.addWidget(self.btn_capture)

        # Stop Video
        self.btn_stop_video = QPushButton()
        self.btn_stop_video.setObjectName("MediaBtn")
        self.btn_stop_video.setIcon(self._load_icon(self.icon_stop_video))
        self.btn_stop_video.setIconSize(QSize(35, 35))
        self.btn_stop_video.setFixedSize(50, 50)
        self.btn_stop_video.setVisible(False)
        self.btn_stop_video.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop_video.setToolTip("Stop Video")
        media_layout.addWidget(self.btn_stop_video)

        # Pause
        self.btn_pause = QPushButton()
        self.btn_pause.setObjectName("MediaBtn")
        self.btn_pause.setIcon(self._load_icon(self.icon_pause_video))
        self.btn_pause.setIconSize(QSize(35, 35))
        self.btn_pause.setFixedSize(50, 50)
        self.btn_pause.setVisible(False)
        self.btn_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pause.setToolTip("Pause Video")
        media_layout.addWidget(self.btn_pause)

        # Resume (Play)
        self.btn_resume = QPushButton()
        self.btn_resume.setObjectName("MediaBtn")
        self.btn_resume.setIcon(self._load_icon(self.icon_play_video))
        self.btn_resume.setIconSize(QSize(35, 35))
        self.btn_resume.setFixedSize(50, 50)
        self.btn_resume.setVisible(False)
        self.btn_resume.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_resume.setToolTip("Play Video")
        media_layout.addWidget(self.btn_resume)

        # Record
        self.btn_record = QPushButton()
        self.btn_record.setObjectName("MediaBtn")
        self.btn_record.setIcon(self._load_icon(self.icon_video_camera))
        self.btn_record.setIconSize(QSize(35, 35))
        self.btn_record.setFixedSize(50, 50)
        self.btn_record.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_record.setToolTip("Record Video")
        media_layout.addWidget(self.btn_record)

        # Recording Time Label
        self.lbl_rec_time = QLabel("00:00:00")
        self.lbl_rec_time.setVisible(False)
        self.lbl_rec_time.setFixedHeight(30)
        self.lbl_rec_time.setMinimumWidth(80)
        self.lbl_rec_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_rec_time.setStyleSheet("""
            background-color: #D3D3D3; 
            border: 2px solid #666666; 
            color: #000000; 
            font-size: 16px; 
            font-weight: bold;
            font-family: monospace;
            border-radius: 0px;
        """)
        media_layout.addWidget(self.lbl_rec_time)
        media_layout.addStretch()

        layout.addWidget(media_group)

    def connect_signals(self):
        self.btn_capture.clicked.connect(self._on_capture_clicked)
        self.btn_record.clicked.connect(self._on_record_clicked)
        self.btn_pause.clicked.connect(self._on_pause_clicked)
        self.btn_resume.clicked.connect(self._on_resume_clicked)
        self.btn_stop_video.clicked.connect(self._on_stop_video_clicked)

    # --- Event handlers ---
    @pyqtSlot()
    def _on_capture_clicked(self):
        if self.current_frame:
            self.capture_requested.emit(self.current_frame)
        else:
            QMessageBox.warning(self, "No Camera Frame", "No photos from the camera yet.")

    @pyqtSlot()
    def _on_record_clicked(self):
        self.record_requested.emit()

    @pyqtSlot()
    def _on_pause_clicked(self):
        self.pause_requested.emit()

    @pyqtSlot()
    def _on_resume_clicked(self):
        self.resume_requested.emit()

    @pyqtSlot()
    def _on_stop_video_clicked(self):
        self.stop_video_requested.emit()

    # --- Public API ---
    def update_frame(self, qimage):
        self.current_frame = qimage

    def set_recording_state(self, state):
        if state == 'idle':
            self.btn_record.setVisible(True)
            self.btn_stop_video.setVisible(False)
            self.btn_pause.setVisible(False)
            self.btn_resume.setVisible(False)
            self.lbl_rec_time.setVisible(False)
            self.btn_capture.setEnabled(True)

        elif state == 'recording':
            self.btn_record.setVisible(False)
            self.btn_stop_video.setVisible(True)
            self.btn_pause.setVisible(True)
            self.btn_resume.setVisible(False)
            self.lbl_rec_time.setVisible(True)
            self.btn_capture.setEnabled(True)

        elif state == 'paused':
            self.btn_record.setVisible(False)
            self.btn_stop_video.setVisible(False)
            self.btn_pause.setVisible(False)
            self.btn_resume.setVisible(True)
            self.lbl_rec_time.setVisible(True)
            self.btn_capture.setEnabled(True)

    def set_recording_time(self, time_str):
        self.lbl_rec_time.setText(time_str)

    def is_capture_enabled(self):
        return self.btn_capture.isEnabled()

    def enable_capture(self, enable=True):
        self.btn_capture.setEnabled(enable)