import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ui.login_page import LoginPage
from ui.camera_page import CameraPage
from ui.register_page import RegisterPage
from ui.records_page import RecordsPage
from utils.face_engine import FaceEngine
from utils.storage import EmployeeStore


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WorkSight")
        self.resize(900, 800)

        self.engine = FaceEngine()      # loaded once, shared by both camera screens
        self.store = EmployeeStore()

        self.login = LoginPage()
        self.camera = CameraPage(self.engine, self.store)
        self.register_page = RegisterPage(self.engine, self.store)
        self.records = RecordsPage()

        self.stack = QStackedWidget()
        for page in (self.login, self.camera, self.register_page, self.records):
            self.stack.addWidget(page)
        self.setCentralWidget(self.stack)

        menu = self.menuBar()
        menu.addAction("Check in/out", lambda: self.show_page(self.camera))
        menu.addAction("Register", lambda: self.show_page(self.register_page))
        menu.addAction("Records", lambda: self.show_page(self.records))
        menu.setVisible(False)          # hidden until logged in

        self.login.login_success.connect(self.after_login)

    def after_login(self):
        self.menuBar().setVisible(True)
        self.show_page(self.camera)

    def show_page(self, page):
        self.camera.stop_camera()
        self.register_page.stop_camera()
        self.stack.setCurrentWidget(page)
        if page is self.camera or page is self.register_page:
            page.start_camera()

    def closeEvent(self, event):
        self.camera.stop_camera()
        self.register_page.stop_camera()
        event.accept()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())