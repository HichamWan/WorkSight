import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ui.login_page import LoginPage
from ui.camera_page import CameraPage
from ui.records_page import RecordsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WorkSight")
        self.resize(900, 650)

        self.login = LoginPage()
        self.camera = CameraPage()
        self.records = RecordsPage()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.login)
        self.stack.addWidget(self.camera)
        self.stack.addWidget(self.records)
        self.setCentralWidget(self.stack)

        menu = self.menuBar()
        menu.addAction("Check in/out", self.show_checkin)
        menu.addAction("Records", self.show_records)
        menu.setVisible(False)  # hidden until logged in

        self.login.login_success.connect(self.show_checkin)

    def show_checkin(self):
        self.menuBar().setVisible(True)
        self.stack.setCurrentWidget(self.camera)
        self.camera.start_camera()

    def show_records(self):
        self.camera.stop_camera()
        self.stack.setCurrentWidget(self.records)

    def closeEvent(self, event):
        self.camera.stop_camera()
        event.accept()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())