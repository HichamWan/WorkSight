import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ui.login_page import LoginPage
from ui.camera_page import CameraPage
from ui.register_page import RegisterPage
from ui.records_page import RecordsPage
from utils.face_engine import FaceEngine
from utils.storage import EmployeeStore
from utils.records import RecordStore
from ui.employee_list_page import EmployeeListPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WorkSight")
        self.resize(900, 800)

        self.engine = FaceEngine()
        self.store = EmployeeStore()
        self.record_store = RecordStore()           # <-- new

        self.login = LoginPage()
        self.camera = CameraPage(self.engine, self.store, self.record_store)   # <-- changed
        self.register_page = RegisterPage(self.engine, self.store)
        self.records = RecordsPage(self.record_store)                          # <-- changed
        self.employee_list = EmployeeListPage(self.store)                     # <-- new

        self.stack = QStackedWidget()
        for page in (self.login, self.camera, self.register_page,
             self.employee_list, self.records):
            self.stack.addWidget(page)
        self.setCentralWidget(self.stack)

        menu = self.menuBar()
        menu.addAction("Check in/out", lambda: self.show_page(self.camera))
        menu.addAction("Register", lambda: self.show_page(self.register_page))
        menu.addAction("Employees", lambda: self.show_page(self.employee_list))
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
        if page is self.records:
            self.records.refresh()                                         # <-- new
        if page is self.employee_list:
            self.employee_list.refresh()

    def closeEvent(self, event):
        self.camera.stop_camera()
        self.register_page.stop_camera()
        event.accept()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())