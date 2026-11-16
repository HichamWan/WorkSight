import json
import os
import numpy as np

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "employees.json")

INFO_KEYS = ("first_name", "last_name", "email", "phone", "department", "position")


class EmployeeStore:
    """Local copy of employees + their face samples. Key = employee code."""

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

    @staticmethod
    def _to_lists(features):
        return [np.asarray(f).flatten().tolist() for f in features]

    @staticmethod
    def _fill_names(emp):
        emp["name"] = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip()
        emp["role"] = emp.get("position", "")

    def exists(self, code):
        return code in self.employees

    def has_face(self, code):
        return bool(self.employees.get(code, {}).get("features"))

    def server_id_of(self, code):
        return self.employees.get(code, {}).get("server_id")

    def add_employee(self, code, server_id, info, features):
        emp = {"server_id": server_id}
        for key in INFO_KEYS:
            emp[key] = info.get(key, "")
        self._fill_names(emp)
        emp["features"] = self._to_lists(features)
        self.employees[code] = emp
        self.save()

    def add_face(self, code, features):
        self.employees[code]["features"] = self._to_lists(features)
        self.save()

    def update_employee(self, code, info):
        emp = self.employees[code]
        emp.update(info)
        self._fill_names(emp)
        self.save()

    def delete_employee(self, code):
        if code in self.employees:
            del self.employees[code]
            self.save()

    def name_of(self, code):
        return self.employees[code]["name"]

    def sync_from_server(self, server_list):
        """Mirror the server's employee list, keeping our local face samples."""
        seen = set()
        for e in server_list:
            code = e["employee_code"]
            seen.add(code)
            old_features = self.employees.get(code, {}).get("features", [])
            emp = {"server_id": e["id"]}
            for key in INFO_KEYS:
                emp[key] = e.get(key, "") or ""
            self._fill_names(emp)
            emp["features"] = old_features
            self.employees[code] = emp
        # removed on the server -> remove here too (local-only ones are kept)
        for code in list(self.employees):
            if self.employees[code].get("server_id") is not None and code not in seen:
                del self.employees[code]
        self.save()

    def get_known(self):
        """Returns {code: [feature, ...]} for the face engine (only people with faces)."""
        return {
            code: [np.array(f, dtype=np.float32).reshape(1, -1)
                   for f in emp["features"]]
            for code, emp in self.employees.items()
            if emp.get("features")
        }