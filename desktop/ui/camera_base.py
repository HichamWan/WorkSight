import cv2
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap

FAIL_LIMIT = 30      # failed reads in a row (about 1 second) before the camera counts as lost
RETRY_MS = 2000      # how often to try to reopen a missing camera


class CameraWidget(QWidget):
    """Camera preview shared by screens. Subclasses override on_frame()."""

    def __init__(self):
        super().__init__()
        self.video = QLabel("Camera off")
        self.video.setAlignment(Qt.AlignCenter)
        self.video.setFixedSize(640, 480)
        self.video.setObjectName("video")

        self.cap = None
        self.wanted = False        # the current screen wants the camera on
        self.fail_count = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.retry_timer = QTimer()
        self.retry_timer.setInterval(RETRY_MS)
        self.retry_timer.timeout.connect(self._try_open)

    def start_camera(self):
        self.wanted = True
        if self.cap is not None:
            return
        self._try_open()

    def _try_open(self):
        if not self.wanted or self.cap is not None:
            return
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            self.cap = cap
            self.fail_count = 0
            self.retry_timer.stop()
            self.timer.start(33)
        else:
            cap.release()
            self.video.setText("Camera not found. Retrying...")
            if not self.retry_timer.isActive():
                self.retry_timer.start()

    def stop_camera(self):
        self.wanted = False
        self.timer.stop()
        self.retry_timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.video.setText("Camera off")

    def _lost(self):
        """The camera stopped giving frames (unplugged, taken by another app...)."""
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.video.setText("Camera disconnected. Reconnecting...")
        self.retry_timer.start()

    def on_frame(self, frame):
        """Draw on the frame and return it. Override in subclasses."""
        return frame

    def _tick(self):
        if self.cap is None:
            return
        ok, frame = self.cap.read()
        if not ok:
            self.fail_count += 1
            if self.fail_count >= FAIL_LIMIT:
                self._lost()
            return
        self.fail_count = 0
        frame = self.on_frame(frame)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
        self.video.setPixmap(QPixmap.fromImage(image).scaled(
            self.video.size(), Qt.KeepAspectRatio))