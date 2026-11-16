import json
import os
import numpy as np

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "employees.json")


class EmployeeStore:
    """Saves employees (id, name, role, face samples) in a local JSON file."""

    def __init__(self, path=DATA_FILE):
        self.path = path
        self.employees = {}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.employees = json.load(f)

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.employees, f, ensure_ascii=False)

    def exists(self, emp_id):
        return emp_id in self.employees

    def add_employee(self, emp_id, name, role, features):
        self.employees[emp_id] = {
            "name": name,
            "role": role,
            "features": [np.asarray(f).flatten().tolist() for f in features],
        }
        self.save()

    def name_of(self, emp_id):
        return self.employees[emp_id]["name"]

    def update_employee(self, emp_id, name, role):
        self.employees[emp_id]["name"] = name
        self.employees[emp_id]["role"] = role
        self.save()

    def delete_employee(self, emp_id):
        if emp_id in self.employees:
            del self.employees[emp_id]
            self.save()

    def get_known(self):
        """Returns {id: [feature, ...]} in the format the face engine needs."""
        return {
            emp_id: [np.array(f, dtype=np.float32).reshape(1, -1)
                     for f in emp["features"]]
            for emp_id, emp in self.employees.items()
        }

    