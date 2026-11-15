import os
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "models")
YUNET_PATH = os.path.join(MODEL_DIR, "face_detection_yunet_2023mar.onnx")


class CameraPage(QWidget):
    def __init__(self):
        super().__init__()

        self.video = QLabel("Camera off")
        self.video.setAlignment(Qt.AlignCenter)
        self.video.setFixedSize(640, 480)
        self.video.setStyleSheet("background-color: #222; color: white;")

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.video, alignment=Qt.AlignCenter)
        layout.addWidget(self.status)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.frame_count = 0
        self.last_faces = []
        self.detector = None
        if os.path.exists(YUNET_PATH):
            self.detector = cv2.FaceDetectorYN.create(
                YUNET_PATH, "", (320, 320), 0.8, 0.3, 5000)
        else:
            self.status.setText("YuNet model file not found in assets/models")

    def start_camera(self):
        if self.cap is not None:
            return
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.video.setText("Could not open camera")
            self.cap = None
            return
        self.timer.start(33)

    def stop_camera(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.video.setText("Camera off")

    def detect_faces(self, frame):
        h, w = frame.shape[:2]
        self.detector.setInputSize((w, h))
        _, faces = self.detector.detect(frame)
        return [] if faces is None else faces

    def update_frame(self):
        ok, frame = self.cap.read()
        if not ok:
            return

        if self.detector is not None:
            self.frame_count += 1
            if self.frame_count % 3 == 0:        # detect every 3rd frame
                self.last_faces = self.detect_faces(frame)

            for f in self.last_faces:
                x, y, fw, fh = f[:4].astype(int)
                cv2.rectangle(frame, (x, y), (x + fw, y + fh), (0, 255, 0), 2)
            self.status.setText(f"Faces detected: {len(self.last_faces)}")

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
        self.video.setPixmap(QPixmap.fromImage(image).scaled(
            self.video.size(), Qt.KeepAspectRatio))