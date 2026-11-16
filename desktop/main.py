import os
STYLE_FILE = os.path.join(os.path.dirname(__file__), "assets", "style.qss")
import sys
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtGui import QCursor, QKeySequence, QShortcut
from PySide6.QtCore import QTimer
import config
from ui.login_page import LoginPage
from ui.camera_page import CameraPage
from ui.register_page import RegisterPage
from ui.records_page import RecordsPage
from ui.employee_list_page import EmployeeListPage
from utils.face_engine import FaceEngine
from utils.storage import EmployeeStore
from utils.records import RecordStore

FULLSCREEN = getattr(config, "FULLSCREEN", True)
MENU_HIDE_SECONDS = getattr(config, "MENU_HIDE_SECONDS", 15)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WorkSight")
        self.resize(900, 800)

        self.engine = FaceEngine()
        self.store = EmployeeStore()
        self.record_store = RecordStore()

        self.login = LoginPage()
        self.camera = CameraPage(self.engine, self.store, self.record_store)
        self.register_page = RegisterPage(self.engine, self.store)
        self.records = RecordsPage(self.record_store, self.store)
        self.employee_list = EmployeeListPage(self.store)

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

        # kiosk helpers
        self.logged_in = False
        self.last_cursor = QCursor.pos()
        self.last_move = time.time()
        self.idle_timer = QTimer(self)
        self.idle_timer.setInterval(500)
        self.idle_timer.timeout.connect(self.check_idle)
        self.idle_timer.start()
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Esc"), self, self.leave_fullscreen)

    def after_login(self):
        self.logged_in = True
        self.last_move = time.time()
        self.menuBar().setVisible(True)
        if FULLSCREEN:
            self.showFullScreen()
        self.show_page(self.camera)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def leave_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()

    def check_idle(self):
        """Hide the menu on the camera page when nobody moves the mouse."""
        if not self.logged_in:
            return
        pos = QCursor.pos()
        if pos != self.last_cursor:
            self.last_cursor = pos
            self.last_move = time.time()
            if not self.menuBar().isVisible():
                self.menuBar().setVisible(True)
        elif (self.stack.currentWidget() is self.camera
              and time.time() - self.last_move > MENU_HIDE_SECONDS):
            if self.menuBar().isVisible():
                self.menuBar().setVisible(False)

    def show_page(self, page):
        self.camera.stop_camera()
        self.register_page.stop_camera()
        self.stack.setCurrentWidget(page)
        self.last_move = time.time()
        if page is self.camera or page is self.register_page:
            page.start_camera()
        if page is self.records:
            self.records.refresh()
        if page is self.employee_list:
            self.employee_list.refresh()

    def closeEvent(self, event):
        self.camera.stop_camera()
        self.register_page.stop_camera()
        event.accept()


app = QApplication(sys.argv)
app.setStyle("Fusion")        # makes the stylesheet render the same on every PC
try:
    with open(STYLE_FILE, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
except FileNotFoundError:
    print("style.qss not found, using the default look")
window = MainWindow()
window.show()
sys.exit(app.exec())