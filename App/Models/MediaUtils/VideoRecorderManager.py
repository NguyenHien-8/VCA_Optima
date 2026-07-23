# App/Models/MediaUtils/VideoRecorderManager.py
import os
import cv2
import numpy as np
from enum import Enum
from datetime import datetime
from collections import deque
from PyQt6.QtCore import QThread, QMutex, QWaitCondition

class VideoState(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"


class VideoRecorderThread(QThread):
    def __init__(self, save_path, fps=30.0, max_queue_size=5):
        super().__init__()
        self.save_path = save_path
        self.fps = fps
        self.max_queue_size = max_queue_size
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.running = True
        self.paused = False
        self.writer = None
        self.frame_queue = deque(maxlen=max_queue_size)

    def update_frame(self, qimage):
        """Receive QImage from the main thread and place it in the queue (thread-safe)."""
        if qimage is None or qimage.isNull():
            return
        frame_copy = qimage.copy()
        self.mutex.lock()
        self.frame_queue.append(frame_copy)
        self.condition.wakeOne()
        self.mutex.unlock()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
        self.condition.wakeAll()

    def stop(self):
        self.running = False
        self.mutex.lock()
        self.condition.wakeOne()
        self.mutex.unlock()
        self.wait()

    def run(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = None
        while self.running:
            qimage = None
            self.mutex.lock()
            if self.paused or len(self.frame_queue) == 0:
                self.condition.wait(self.mutex, 100)
                self.mutex.unlock()
                continue

            # Only take the latest frame, discard older frames if the queue is congested.
            while len(self.frame_queue) > 1:
                self.frame_queue.popleft()
            qimage = self.frame_queue.popleft()
            self.mutex.unlock()

            # Convert QImage → numpy BGR (run in write stream)
            frame_bgr = self._qimage_to_bgr_numpy(qimage)
            if frame_bgr is None:
                continue

            if self.writer is None:
                h, w = frame_bgr.shape[:2]
                self.writer = cv2.VideoWriter(self.save_path, fourcc, self.fps, (w, h))

            if self.writer:
                self.writer.write(frame_bgr)

        if self.writer:
            self.writer.release()

    @staticmethod
    def _qimage_to_bgr_numpy(qimage):
        """Convert QImage (RGB) to numpy array (BGR)"""
        if qimage is None or qimage.isNull():
            return None
        try:
            width = qimage.width()
            height = qimage.height()
            ptr = qimage.bits()
            ptr.setsize(height * width * 3)
            arr_rgb = np.array(ptr).reshape(height, width, 3)
            return cv2.cvtColor(arr_rgb, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"[VideoRecorderThread] Conversion error: {e}")
            return None


class FolderManager:
    @staticmethod
    def ensure_folder_exists(folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
            return True, f"Folder ready: {folder_path}"
        except OSError as e:
            return False, f"Cannot create folder: {str(e)}"


class VideoRecorderManager:
    def __init__(self, item_path):
        self.item_path = item_path
        self.video_folder = os.path.join(item_path, "Video")
        FolderManager.ensure_folder_exists(self.video_folder)

        self.video_thread = None
        self.video_state = VideoState.IDLE
        self.current_video_path = None

    def start_video(self, fps=20.0):
        if self.video_state != VideoState.IDLE:
            return False, "", "Video is already recording or paused"

        try:
            if not os.path.exists(self.item_path):
                return False, "", "Item path is invalid or does not exist"

            success, msg = FolderManager.ensure_folder_exists(self.video_folder)
            if not success:
                return False, "", msg

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.mp4"
            self.current_video_path = os.path.join(self.video_folder, filename)

            self.video_thread = VideoRecorderThread(self.current_video_path, fps=fps)
            self.video_thread.start()
            self.video_state = VideoState.RECORDING

            return True, filename, f"Recording started: {filename}"

        except Exception as e:
            self.video_state = VideoState.IDLE
            return False, "", f"Error starting video recording: {str(e)}"

    def pause_video(self):
        if self.video_state == VideoState.RECORDING and self.video_thread:
            self.video_thread.pause()
            self.video_state = VideoState.PAUSED
            return True
        return False

    def resume_video(self):
        if self.video_state == VideoState.PAUSED and self.video_thread:
            self.video_thread.resume()
            self.video_state = VideoState.RECORDING
            return True
        return False

    def stop_video(self):
        if self.video_thread and self.video_state != VideoState.IDLE:
            try:
                self.video_thread.stop()
                self.video_thread = None
                self.video_state = VideoState.IDLE

                if self.current_video_path and os.path.exists(self.current_video_path):
                    filename = os.path.basename(self.current_video_path)
                    return True, filename, f"Video saved successfully: {filename}"
                else:
                    return False, "", "Video recording stopped but file not found"
            except Exception as e:
                self.video_state = VideoState.IDLE
                return False, "", f"Error stopping video: {str(e)}"
        return False, "", "No video is currently recording"

    def get_video_state(self):
        return self.video_state.value if self.video_state else VideoState.IDLE.value

    def is_recording(self):
        return self.video_state != VideoState.IDLE

    def update_video_frame(self, qimage):
        """Send QImage to the recording stream (only while recording is in progress)"""
        if self.video_state == VideoState.RECORDING and self.video_thread:
            self.video_thread.update_frame(qimage)

    def close(self):
        if self.video_state != VideoState.IDLE:
            self.stop_video()