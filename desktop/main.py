import sys

from PySide6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    # TODO: from views.main_window import MainWindow; window = MainWindow(); window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
