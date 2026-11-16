import cv2
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                               QLineEdit, QPushButton)
from PySide6.QtCore import Qt
from ui.camera_base import CameraWidget
from api.client import api
from workers.api_worker import run_async

SAMPLES_NEEDED = 5
BUTTON_TEXT = "Capture face and register"


class RegisterPage(CameraWidget):
    def __init__(self, engine, store):
        super().__init__()
        self.engine = engine
        self.store = store

        self.capturing = False
        self.samples = []
        self.pending = None
        self.created = False        # employee already created on the server
        self.upload_failed = False  # lets the button retry the upload
        self.frame_count = 0
        self.last_faces = []

        title = QLabel("Register employee")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        self.code_input = QLineEdit()
        self.first_input = QLineEdit()
        self.last_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.department_input = QLineEdit()
        self.position_input = QLineEdit()
        self.inputs = (self.code_input, self.first_input, self.last_input,
                       self.email_input, self.phone_input,
                       self.department_input, self.position_input)

        form_box = QWidget()
        form_box.setMaximumWidth(400)
        form = QFormLayout(form_box)
        form.addRow("Employee code", self.code_input)
        form.addRow("First name", self.first_input)
        form.addRow("Last name", self.last_input)
        form.addRow("Email", self.email_input)
        form.addRow("Phone", self.phone_input)
        form.addRow("Department", self.department_input)
        form.addRow("Position", self.position_input)

        self.register_button = QPushButton(BUTTON_TEXT)
        self.register_button.clicked.connect(self.begin_capture)

        self.message = QLabel("")
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self.video, alignment=Qt.AlignCenter)
        layout.addWidget(form_box, alignment=Qt.AlignCenter)
        layout.addWidget(self.register_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.message)

    # ---------- camera ----------
    def start_camera(self):
        self.capturing = False
        self.created = False
        self.upload_failed = False
        self.register_button.setText(BUTTON_TEXT)
        self.register_button.setEnabled(True)
        self.message.setText("")
        super().start_camera()

    def stop_camera(self):
        self.capturing = False
        super().stop_camera()

    def show_message(self, text, error=False):
        self.message.setStyleSheet("color: red;" if error else "")
        self.message.setText(text)

    # ---------- starting ----------
    def read_info(self):
        return {
            "first_name": self.first_input.text().strip(),
            "last_name": self.last_input.text().strip(),
            "email": self.email_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "department": self.department_input.text().strip(),
            "position": self.position_input.text().strip(),
        }

    def begin_capture(self):
        if self.upload_failed:          # button is acting as "Retry upload"
            self.upload()
            return

        code = self.code_input.text().strip()
        if not code:
            self.show_message("Please enter the employee code.", error=True)
            return

        if self.store.exists(code):
            if self.store.has_face(code):
                self.show_message(f"{code} already has a face registered.", error=True)
                return
            # employee is already on the server, we only add the face
            self.pending = {"code": code, "attach": True}
        else:
            info = self.read_info()
            if not all(info.values()):
                self.show_message("Please fill in every field.", error=True)
                return
            if "@" not in info["email"]:
                self.show_message("Please enter a valid email.", error=True)
                return
            self.pending = {"code": code, "attach": False, "info": info}

        self.samples = []
        self.created = False
        self.capturing = True
        self.register_button.setEnabled(False)
        self.show_message(
            f"Look at the camera and slowly turn your head... 0/{SAMPLES_NEEDED}")

    # ---------- finishing ----------
    def finish_capture(self):
        self.capturing = False
        if self.pending["attach"]:
            code = self.pending["code"]
            self.store.add_face(code, self.samples)
            self.done(f"Face added for {self.store.name_of(code)} ({code}).")
        else:
            self.upload()

    def upload(self):
        self.upload_failed = False
        self.register_button.setEnabled(False)
        self.register_button.setText("Saving to server...")
        if self.created:
            self.after_create(None)
            return
        body = {"employee_code": self.pending["code"], **self.pending["info"]}
        run_async(api.request, self.after_create, self.upload_error,
                  "POST", "/hr/employees", json=body)

    def after_create(self, _result):
        self.created = True
        # ask for the list so we learn the new employee's server id
        run_async(api.request, self.after_list, self.upload_error,
                  "GET", "/hr/employees")

    def after_list(self, data):
        code = self.pending["code"]
        match = next((e for e in data.get("employees", [])
                      if e["employee_code"] == code), None)
        if match is None:
            self.upload_error("Saved on the server, but the employee was not found.")
            return
        self.store.add_employee(code, match["id"], self.pending["info"], self.samples)
        name = self.store.name_of(code)
        self.done(f"Registered {name} ({code}).")

    def upload_error(self, message):
        self.upload_failed = True
        self.register_button.setText("Retry upload")
        self.register_button.setEnabled(True)
        self.show_message(
            f"Could not save: {message}. Your face scan is kept. "
            "Press the button to retry. If the code already exists on the server, "
            "open the Employees page once, then register the face again.",
            error=True)

    def done(self, text):
        for box in self.inputs:
            box.clear()
        self.pending = None
        self.samples = []
        self.created = False
        self.upload_failed = False
        self.register_button.setText(BUTTON_TEXT)
        self.register_button.setEnabled(True)
        self.show_message(text)

    # ---------- every frame ----------
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