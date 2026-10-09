from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                               QTableWidgetItem, QPushButton, QHeaderView)


class RecordsPage(QWidget):
    def __init__(self):
        super().__init__()

        title = QLabel("Record History")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Employee ID", "Name", "Type", "Time", "Sync status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # read-only

        sync_button = QPushButton("Sync now")
        sync_button.clicked.connect(self.sync_now)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self.table)
        layout.addWidget(sync_button)

        self.load_sample_data()

    def load_sample_data(self):
        rows = [
            ("1001", "Bat", "Check in", "09:01", "Synced"),
            ("1002", "Sara", "Check in", "09:05", "Not synced"),
            ("1001", "Bat", "Check out", "18:02", "Not synced"),
        ]
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(value))

    def sync_now(self):
        print("Sync clicked (will connect to server later)")