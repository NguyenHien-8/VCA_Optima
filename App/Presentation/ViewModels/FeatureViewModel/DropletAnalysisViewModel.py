import numpy as np

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

from App.Presentation.ViewModels.Workers import FunctionWorker


class DropletAnalysisViewModel(QObject):
    analysis_completed = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    image_loaded = pyqtSignal(QPixmap)
    image_data_ready = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pixmap = None
        self.image_array = None
        self.analysis_data = None
        self._workers = set()

    def load_image_from_pixmap(self, pixmap):
        if pixmap is None or pixmap.isNull():
            self.error_occurred.emit("Invalid image provided")
            return False

        self.current_pixmap = pixmap
        image = pixmap.toImage().convertToFormat(QImage.Format.Format_Grayscale8)
        self._start_worker(
            lambda: self._qimage_to_array(image),
            self._on_image_array_ready,
        )
        return True

    @staticmethod
    def _qimage_to_array(image):
        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())
        rows = np.frombuffer(ptr, dtype=np.uint8).reshape(
            image.height(), image.bytesPerLine()
        )
        return rows[:, : image.width()].copy()

    def _on_image_array_ready(self, image_array):
        self.image_array = image_array
        self.image_loaded.emit(self.current_pixmap)
        self.image_data_ready.emit()

    def perform_analysis(self):
        if self.image_array is None:
            self.error_occurred.emit("No image data to analyze")
            return False

        image_array = self.image_array

        def analyze():
            img_min = np.min(image_array)
            img_max = np.max(image_array)
            if img_max > img_min:
                normalized = (
                    (image_array - img_min) / (img_max - img_min) * 255
                )
            else:
                normalized = image_array.copy()
            return {
                "image": image_array,
                "normalized": normalized,
                "min_value": float(img_min),
                "max_value": float(img_max),
                "mean_value": float(np.mean(image_array)),
                "std_value": float(np.std(image_array)),
                "height": image_array.shape[0],
                "width": image_array.shape[1],
            }

        self._start_worker(analyze, self._on_analysis_ready)
        return True

    def _on_analysis_ready(self, analysis_data):
        self.analysis_data = analysis_data
        self.analysis_completed.emit(analysis_data)

    def _start_worker(self, function, callback):
        worker = FunctionWorker(function)
        self._workers.add(worker)
        worker.result_ready.connect(callback)
        worker.error_occurred.connect(self.error_occurred)
        worker.finished.connect(lambda: self._finish_worker(worker))
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def _finish_worker(self, worker):
        self._workers.discard(worker)

    def get_analysis_data(self):
        return self.analysis_data

    def get_heatmap_data(self):
        if self.analysis_data is None:
            return None
        image = self.analysis_data["normalized"]
        height, width = image.shape
        x = np.linspace(0, 5.0, width)
        y = np.linspace(3.0, 0.0, height)
        x_grid, y_grid = np.meshgrid(x, y)
        return x_grid, y_grid, image

    def close(self):
        for worker in list(self._workers):
            if worker.isRunning():
                worker.requestInterruption()
