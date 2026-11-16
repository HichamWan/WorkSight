from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QHeaderView, QDialog, QFormLayout, QLineEdit,
                               QDialogButtonBox, QMessageBox, QAbstractItemView)


class EditDialog(QDialog):
    """Small pop-up for editing one employee's name and role."""

    def __init__(self, emp_id, name, role, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit employee {emp_id}")
        self.name_input = QLineEdit(name)
        self.role_input = QLineEdit(role)

        form = QFormLayout()
        form.addRow("Name", self.name_input)
        form.addRow("Role", self.role_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self):
        return self.name_input.text().strip(), self.role_input.text().strip()


class EmployeeListPage(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store

        title = QLabel("Employee list")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Employee ID", "Name", "Role", "Face samples"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        edit_button = QPushButton("Edit selected")
        edit_button.clicked.connect(self.edit_selected)
        delete_button = QPushButton("Delete selected")
        delete_button.clicked.connect(self.delete_selected)

        self.message = QLabel("")

        buttons = QHBoxLayout()
        buttons.addWidget(edit_button)
        buttons.addWidget(delete_button)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self.table)
        layout.addLayout(buttons)
        layout.addWidget(self.message)

    def refresh(self):
        self.table.setRowCount(0)
        for emp_id, emp in sorted(self.store.employees.items()):
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = (emp_id, emp["name"], emp["role"], str(len(emp["features"])))
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            self.message.setStyleSheet("color: red;")
            self.message.setText("Select an employee first.")
            return None
        return self.table.item(row, 0).text()

    def edit_selected(self):
        emp_id = self.selected_id()
        if emp_id is None:
            return
        emp = self.store.employees[emp_id]
        dialog = EditDialog(emp_id, emp["name"], emp["role"], self)
        if dialog.exec() == QDialog.Accepted:
            name, role = dialog.values()
            if not name or not role:
                self.message.setStyleSheet("color: red;")
                self.message.setText("Name and role cannot be empty.")
                return
            self.store.update_employee(emp_id, name, role)
            self.message.setStyleSheet("")
            self.message.setText(f"Updated {name}.")
            self.refresh()

    def delete_selected(self):
        emp_id = self.selected_id()
        if emp_id is None:
            return
        name = self.store.name_of(emp_id)
        answer = QMessageBox.question(
            self, "Delete employee",
            f"Delete {name} (ID {emp_id})?\n"
            "Their face data will be removed and they will no longer be recognized.")
        if answer == QMessageBox.Yes:
            self.store.delete_employee(emp_id)
            self.message.setStyleSheet("")
            self.message.setText(f"Deleted {name}.")
            self.refresh()