import os
import cv2
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
from utils.face_engine import FaceEngine

TEST_FACE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "assets", "test_face.npy")


class CameraPage(QWidget):
    def __init__(self):
        super().__init__()

        self.video = QLabel("Camera off")
        self.video.setAlignment(Qt.AlignCenter)
        self.video.setFixedSize(640, 480)
        self.video.setStyleSheet("background-color: #222; color: white;")

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)

        self.save_button = QPushButton("Save my face (test)")
        self.save_button.clicked.connect(self.save_test_face)

        layout = QVBoxLayout(self)
        layout.addWidget(self.video, alignment=Qt.AlignCenter)
        layout.addWidget(self.status)
        layout.addWidget(self.save_button, alignment=Qt.AlignCenter)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.frame_count = 0
        self.last_frame = None
        self.last_faces = []
        self.last_label = ""
        self.last_matched = False

        self.known = {}
        if os.path.exists(TEST_FACE_FILE):
            self.known["me"] = np.load(TEST_FACE_FILE)

        self.engine = None
        try:
            self.engine = FaceEngine()
        except Exception as e:
            self.status.setText(f"Could not load models: {e}")

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

    def save_test_face(self):
        if self.engine is None or self.last_frame is None or not self.last_faces:
            self.status.setText("No face in view. Look at the camera and try again.")
            return
        # use the biggest face in view
        face = max(self.last_faces, key=lambda f: f[2] * f[3])
        feature = self.engine.embed(self.last_frame, face)
        np.save(TEST_FACE_FILE, feature)
        self.known["me"] = feature
        self.status.setText("Face saved. Now you should be recognized.")

    def update_frame(self):
        ok, frame = self.cap.read()
        if not ok:
            return
        self.last_frame = frame.copy()   # clean copy, before drawing on it

        if self.engine is not None:
            self.frame_count += 1
            if self.frame_count % 3 == 0:   # detect + recognize every 3rd frame
                self.last_faces = self.engine.detect(frame)
                self.last_label = ""
                if self.last_faces and self.known:
                    face = max(self.last_faces, key=lambda f: f[2] * f[3])
                    feature = self.engine.embed(frame, face)
                    name, score = self.engine.identify(feature, self.known)
                    self.last_matched = name is not None
                    self.last_label = (f"{name} ({score:.2f})" if name
                                       else f"Unknown ({score:.2f})")

            for f in self.last_faces:
                x, y, fw, fh = f[:4].astype(int)
                color = (0, 255, 0) if self.last_matched else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x + fw, y + fh), color, 2)
                if self.last_label:
                    cv2.putText(frame, self.last_label, (x, max(y - 8, 15)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
        self.video.setPixmap(QPixmap.fromImage(image).scaled(
            self.video.size(), Qt.KeepAspectRatio))