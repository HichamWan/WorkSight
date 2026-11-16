from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                               QTableWidgetItem, QPushButton, QHeaderView)
from workers.api_worker import run_async
from utils.sync import send_records


class RecordsPage(QWidget):
    def __init__(self, records, store):
        super().__init__()
        self.records = records
        self.store = store

        title = QLabel("Record History")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Employee ID", "Name", "Type", "Time", "Sync status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.sync_button = QPushButton("Sync now")
        self.sync_button.setObjectName("primary")
        self.sync_button.clicked.connect(self.sync_now)

        self.message = QLabel("")
        self.message.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self.table)
        layout.addWidget(self.sync_button)
        layout.addWidget(self.message)

    def say(self, text, error=False):
        self.message.setStyleSheet("color: red;" if error else "")
        self.message.setText(text)

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
        pending = self.records.pending()
        if not pending:
            self.say("Everything is already synced.")
            return
        id_map = {code: emp.get("server_id")
                  for code, emp in self.store.employees.items()}
        self.sync_button.setEnabled(False)
        self.sync_button.setText("Syncing...")
        self.say("")
        run_async(send_records, self.after_sync, self.sync_failed, pending, id_map)

    def after_sync(self, result):
        self.records.mark_synced(result["synced"])
        self.sync_button.setEnabled(True)
        self.sync_button.setText("Sync now")
        self.refresh()

        sent = len(result["synced"])
        failed = result["failed"]
        left = result["total"] - sent - len(failed)
        text = f"Synced {sent} record(s)."
        if failed:
            text += f" {len(failed)} failed: {failed[0][1]}."
        if left:
            text += f" {left} not tried yet, press Sync again later."
        self.say(text, error=bool(failed or left))

    def sync_failed(self, message):
        self.sync_button.setEnabled(True)
        self.sync_button.setText("Sync now")
        self.say(f"Sync failed: {message}", error=True)