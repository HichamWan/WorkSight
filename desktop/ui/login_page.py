from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Signal, Qt


class LoginPage(QWidget):
    login_success = Signal()   # tells the main window "login worked"

    def __init__(self):
        super().__init__()

        title = QLabel("WorkSight")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        self.company = QLineEdit()
        self.company.setPlaceholderText("Company name")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.error = QLabel("")
        self.error.setStyleSheet("color: red;")
        self.error.setAlignment(Qt.AlignCenter)

        button = QPushButton("Login")
        button.clicked.connect(self.try_login)
        self.password.returnPressed.connect(self.try_login)  # Enter key works too

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        for w in (title, self.company, self.password, self.error, button):
            w.setMaximumWidth(320)
            layout.addWidget(w, alignment=Qt.AlignCenter)

    def try_login(self):
        if not self.company.text().strip() or not self.password.text():
            self.error.setText("Please enter company name and password")
            return
        # TODO: later, check these against the server
        self.error.setText("")
        self.login_success.emit()