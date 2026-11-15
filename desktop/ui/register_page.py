import cv2
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                               QLineEdit, QPushButton)
from PySide6.QtCore import Qt
from ui.camera_base import CameraWidget

SAMPLES_NEEDED = 5


class RegisterPage(CameraWidget):
    def __init__(self, engine, store):
        super().__init__()
        self.engine = engine
        self.store = store

        self.capturing = False
        self.samples = []
        self.pending = None
        self.frame_count = 0
        self.last_faces = []

        title = QLabel("Register employee")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        self.id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.role_input = QLineEdit()
        form_box = QWidget()
        form_box.setMaximumWidth(400)
        form = QFormLayout(form_box)
        form.addRow("Employee ID", self.id_input)
        form.addRow("Name", self.name_input)
        form.addRow("Role", self.role_input)

        self.register_button = QPushButton("Capture face and register")
        self.register_button.clicked.connect(self.begin_capture)

        self.message = QLabel("")
        self.message.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self.video, alignment=Qt.AlignCenter)
        layout.addWidget(form_box, alignment=Qt.AlignCenter)
        layout.addWidget(self.register_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.message)

    def start_camera(self):
        self.capturing = False
        self.register_button.setEnabled(True)
        self.message.setText("")
        super().start_camera()

    def stop_camera(self):
        self.capturing = False
        super().stop_camera()

    def show_message(self, text, error=False):
        self.message.setStyleSheet("color: red;" if error else "")
        self.message.setText(text)

    def begin_capture(self):
        emp_id = self.id_input.text().strip()
        name = self.name_input.text().strip()
        role = self.role_input.text().strip()
        if not (emp_id and name and role):
            self.show_message("Please fill in ID, name and role.", error=True)
            return
        if self.store.exists(emp_id):
            self.show_message(f"ID {emp_id} is already registered.", error=True)
            return
        self.pending = (emp_id, name, role)
        self.samples = []
        self.capturing = True
        self.register_button.setEnabled(False)
        self.show_message(
            f"Look at the camera and slowly turn your head... 0/{SAMPLES_NEEDED}")

    def finish_capture(self):
        emp_id, name, role = self.pending
        self.store.add_employee(emp_id, name, role, self.samples)
        self.capturing = False
        self.register_button.setEnabled(True)
        for box in (self.id_input, self.name_input, self.role_input):
            box.clear()
        self.show_message(f"Registered {name} (ID {emp_id}).")

    def on_frame(self, frame):
        self.frame_count += 1
        if self.frame_count % 3 == 0:
            self.last_faces = self.engine.detect(frame)

            # take one sample about every 9 frames while capturing
            if self.capturing and self.frame_count % 9 == 0:
                if len(self.last_faces) == 1:
                    self.samples.append(self.engine.embed(frame, self.last_faces[0]))
                    self.show_message(
                        f"Look at the camera and slowly turn your head... "
                        f"{len(self.samples)}/{SAMPLES_NEEDED}")
                    if len(self.samples) >= SAMPLES_NEEDED:
                        self.finish_capture()
                else:
                    self.show_message("Make sure exactly one face is in view.",
                                      error=True)

        for f in self.last_faces:
            x, y, fw, fh = f[:4].astype(int)
            cv2.rectangle(frame, (x, y), (x + fw, y + fh), (255, 160, 0), 2)
        return frame