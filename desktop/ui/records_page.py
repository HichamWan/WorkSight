from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                               QTableWidgetItem, QPushButton, QHeaderView)


class RecordsPage(QWidget):
    def __init__(self, records):
        super().__init__()
        self.records = records

        title = QLabel("Record History")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Employee ID", "Name", "Type", "Time", "Sync status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        sync_button = QPushButton("Sync now")
        sync_button.clicked.connect(self.sync_now)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self.table)
        layout.addWidget(sync_button)

    def refresh(self):
        self.table.setRowCount(0)
        for r in self.records.recent():
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = (r["employee_id"], r["name"], r["type"], r["time"],
                      "Synced" if r["synced"] else "Not synced")
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def sync_now(self):
        print("Sync clicked (will connect to the API in Step 6)")