import time
import cv2
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from ui.camera_base import CameraWidget

CONFIRM_FRAMES = 3      # same person must match this many checks in a row
COOLDOWN_SECONDS = 30   # ignore the same person for this long after a record
BANNER_SECONDS = 4      # how long the result message stays on screen


class CameraPage(CameraWidget):
    def __init__(self, engine, store, records):
        super().__init__()
        self.engine = engine
        self.store = store
        self.records = records

        self.banner = QLabel("")
        self.banner.setAlignment(Qt.AlignCenter)
        self.banner.setMinimumHeight(60)
        self.banner.setStyleSheet("font-size: 20px; font-weight: bold;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.video, alignment=Qt.AlignCenter)
        layout.addWidget(self.banner)

        self.known = {}
        self.frame_count = 0
        self.last_faces = []
        self.last_label = ""
        self.last_matched = False

        self.candidate = None          # who we think is in front of the camera
        self.candidate_count = 0       # how many checks in a row said so
        self.cooldown_until = {}       # employee id -> time they can be recorded again
        self.banner_until = 0

    def show_banner(self, text, color):
        self.banner.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {color};")
        self.banner.setText(text)
        self.banner_until = time.time() + BANNER_SECONDS

    def start_camera(self):
        self.known = self.store.get_known()   # reload, in case someone registered
        self.candidate = None
        self.candidate_count = 0
        if not self.known:
            self.banner.setText("No employees registered yet. Use Register first.")
        else:
            self.banner.setText("")
        super().start_camera()

    def handle_match(self, emp_id, score):
        """Called when a face is recognized. Confirms it, then records it."""
        if emp_id == self.candidate:
            self.candidate_count += 1
        else:
            self.candidate = emp_id
            self.candidate_count = 1

        if self.candidate_count < CONFIRM_FRAMES:
            return

        now = time.time()
        if now < self.cooldown_until.get(emp_id, 0):
            return    # recorded recently, ignore

        record = self.records.add(emp_id, self.store.name_of(emp_id), score)
        self.cooldown_until[emp_id] = now + COOLDOWN_SECONDS
        clock = record["time"][11:16]
        color = "#2e9e4f" if record["type"] == "Check in" else "#d98a00"
        self.show_banner(f'{record["name"]}: {record["type"]} at {clock}', color)

    def on_frame(self, frame):
        # clear the banner after a few seconds
        if self.banner_until and time.time() > self.banner_until:
            self.banner.setText("")
            self.banner_until = 0

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
                    self.handle_match(emp_id, score)
                else:
                    self.last_label = f"Unknown ({score:.2f})"
                    self.candidate = None
                    self.candidate_count = 0
            else:
                self.candidate = None
                self.candidate_count = 0

        for f in self.last_faces:
            x, y, fw, fh = f[:4].astype(int)
            color = (0, 255, 0) if self.last_matched else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x + fw, y + fh), color, 2)
            if self.last_label:
                cv2.putText(frame, self.last_label, (x, max(y - 8, 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return frame