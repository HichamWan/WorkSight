from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QHeaderView, QDialog, QFormLayout, QLineEdit,
                               QDialogButtonBox, QMessageBox, QAbstractItemView)
from api.client import api
from workers.api_worker import run_async

FIELDS = [("first_name", "First name"), ("last_name", "Last name"),
          ("email", "Email"), ("phone", "Phone"),
          ("department", "Department"), ("position", "Position")]


class EditDialog(QDialog):
    """Pop-up for editing one employee's details."""

    def __init__(self, code, emp, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit employee {code}")
        self.inputs = {}
        form = QFormLayout()
        for key, label in FIELDS:
            box = QLineEdit(emp.get(key, ""))
            self.inputs[key] = box
            form.addRow(label, box)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self):
        return {key: box.text().strip() for key, box in self.inputs.items()}


class EmployeeListPage(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store

        title = QLabel("Employee list")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Code", "Name", "Position", "Department", "Face samples", "On server"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        edit_button = QPushButton("Edit selected")
        edit_button.clicked.connect(self.edit_selected)
        delete_button = QPushButton("Delete selected")
        delete_button.clicked.connect(self.delete_selected)

        self.message = QLabel("")
        self.message.setWordWrap(True)

        buttons = QHBoxLayout()
        buttons.addWidget(edit_button)
        buttons.addWidget(delete_button)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self.table)
        layout.addLayout(buttons)
        layout.addWidget(self.message)

    # ---------- showing ----------
    def say(self, text, error=False):
        self.message.setStyleSheet("color: red;" if error else "")
        self.message.setText(text)

    def refresh(self):
        self.draw()                       # show saved data right away
        self.say("Loading from server...")
        run_async(api.request, self.after_fetch, self.fetch_failed,
                  "GET", "/hr/employees")

    def after_fetch(self, data):
        self.store.sync_from_server(data.get("employees", []))
        self.draw()
        self.say("")

    def fetch_failed(self, message):
        self.say(f"Showing saved data only. {message}", error=True)

    def draw(self):
        self.table.setRowCount(0)
        for code, emp in sorted(self.store.employees.items()):
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = (
                code,
                emp.get("name", ""),
                emp.get("position") or emp.get("role", ""),
                emp.get("department", ""),
                str(len(emp.get("features", []))),
                "Yes" if emp.get("server_id") is not None else "No",
            )
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def selected_code(self):
        row = self.table.currentRow()
        if row < 0:
            self.say("Select an employee first.", error=True)
            return None
        return self.table.item(row, 0).text()

    # ---------- editing ----------
    def edit_selected(self):
        code = self.selected_code()
        if code is None:
            return
        emp = dict(self.store.employees[code])
        # employees made before the server existed only have a single name
        if not emp.get("first_name"):
            emp["first_name"] = emp.get("name", "")
        if not emp.get("position"):
            emp["position"] = emp.get("role", "")

        dialog = EditDialog(code, emp, self)
        if dialog.exec() != QDialog.Accepted:
            return
        info = dialog.values()
        if not info["first_name"] or not info["position"]:
            self.say("First name and position cannot be empty.", error=True)
            return

        server_id = emp.get("server_id")
        if server_id is None:
            self.apply_edit(code, info)
            return
        self.say("Saving to server...")
        body = {"employee_code": code, **info}
        run_async(api.request, lambda _r: self.apply_edit(code, info),
                  lambda m: self.say(f"Could not save: {m}", error=True),
                  "PUT", f"/hr/employees/{server_id}", json=body)

    def apply_edit(self, code, info):
        self.store.update_employee(code, info)
        self.say(f"Updated {self.store.name_of(code)}.")
        self.draw()

    # ---------- deleting ----------
    def delete_selected(self):
        code = self.selected_code()
        if code is None:
            return
        name = self.store.name_of(code)
        answer = QMessageBox.question(
            self, "Delete employee",
            f"Delete {name} ({code})?\n"
            "They will be removed from the server and their face data will be "
            "deleted from this computer.")
        if answer != QMessageBox.Yes:
            return

        server_id = self.store.server_id_of(code)
        if server_id is None:
            self.apply_delete(code, name)
            return
        self.say("Deleting on server...")
        run_async(api.request, lambda _r: self.apply_delete(code, name),
                  lambda m: self.say(f"Could not delete: {m}", error=True),
                  "DELETE", f"/hr/employees/{server_id}")

    def apply_delete(self, code, name):
        self.store.delete_employee(code)
        self.say(f"Deleted {name}.")
        self.draw()