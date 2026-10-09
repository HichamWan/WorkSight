import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap


class CameraPage(QWidget):
    def __init__(self):
        super().__init__()

        self.video = QLabel("Camera off")
        self.video.setAlignment(Qt.AlignCenter)
        self.video.setFixedSize(640, 480)
        self.video.setStyleSheet("background-color: #222; color: white;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.video, alignment=Qt.AlignCenter)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def start_camera(self):
        if self.cap is not None:
            return
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 0 = first camera
        if not self.cap.isOpened():
            self.video.setText("Could not open camera")
            self.cap = None
            return
        self.timer.start(33)  # ~30 frames per second

    def stop_camera(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.video.setText("Camera off")

    def update_frame(self):
        ok, frame = self.cap.read()
        if not ok:
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV uses BGR, Qt wants RGB
        h, w, ch = rgb.shape
        image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
        self.video.setPixmap(QPixmap.fromImage(image).scaled(
            self.video.size(), Qt.KeepAspectRatio))