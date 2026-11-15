import cv2
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from ui.camera_base import CameraWidget


class CameraPage(CameraWidget):
    def __init__(self, engine, store):
        super().__init__()
        self.engine = engine
        self.store = store

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.video, alignment=Qt.AlignCenter)
        layout.addWidget(self.status)

        self.known = {}
        self.frame_count = 0
        self.last_faces = []
        self.last_label = ""
        self.last_matched = False

    def start_camera(self):
        self.known = self.store.get_known()   # reload, in case someone registered
        if not self.known:
            self.status.setText("No employees registered yet. Use Register first.")
        else:
            self.status.setText("")
        super().start_camera()

    def on_frame(self, frame):
        self.frame_count += 1
        if self.frame_count % 3 == 0:
            self.last_faces = self.engine.detect(frame)
            self.last_label = ""
            self.last_matched = False
            if self.last_faces and self.known:
                face = max(self.last_faces, key=lambda f: f[2] * f[3])
                feature = self.engine.embed(frame, face)
                emp_id, score = self.engine.identify(feature, self.known)
                if emp_id is not None:
                    self.last_matched = True
                    self.last_label = f"{self.store.name_of(emp_id)} ({score:.2f})"
                else:
                    self.last_label = f"Unknown ({score:.2f})"

        for f in self.last_faces:
            x, y, fw, fh = f[:4].astype(int)
            color = (0, 255, 0) if self.last_matched else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x + fw, y + fh), color, 2)
            if self.last_label:
                cv2.putText(frame, self.last_label, (x, max(y - 8, 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return frame