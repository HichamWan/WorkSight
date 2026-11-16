from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Signal, Qt

from api.client import api
from workers.api_worker import run_async


class LoginPage(QWidget):
    login_success = Signal()   # tells the main window "login worked"

    def __init__(self):
        super().__init__()

        title = QLabel("WorkSight")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.error = QLabel("")
        self.error.setStyleSheet("color: red;")
        self.error.setAlignment(Qt.AlignCenter)

        self.button = QPushButton("Login")
        self.button.setObjectName("primary")
        self.button.clicked.connect(self.try_login)
        self.username.returnPressed.connect(self.try_login)
        self.password.returnPressed.connect(self.try_login)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        for w in (title, self.username, self.password, self.error, self.button):
            w.setMaximumWidth(320)
            layout.addWidget(w, alignment=Qt.AlignCenter)

    def try_login(self):
        name = self.username.text().strip()
        pw = self.password.text()
        if not name or not pw:
            self.error.setText("Please enter username and password")
            return
        self.error.setText("")
        self.button.setEnabled(False)
        self.button.setText("Logging in...")
        # runs in the background so the window never freezes
        run_async(api.login, self.on_success, self.on_fail, name, pw)

    def on_success(self, _result):
        self._reset_button()
        self.password.clear()
        self.login_success.emit()

    def on_fail(self, message):
        self._reset_button()
        self.error.setText(message)

    def _reset_button(self):
        self.button.setEnabled(True)
        self.button.setText("Login")