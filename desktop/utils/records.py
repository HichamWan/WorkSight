import json
import os
import uuid
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "records.json")


class RecordStore:
    """Saves attendance records in a local JSON file."""

    def __init__(self, path=DATA_FILE):
        self.path = path
        self.records = []
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.records = json.load(f)

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False)

    def next_type_for(self, emp_id):
        """First scan of the day = check in, then it alternates."""
        today = datetime.now().strftime("%Y-%m-%d")
        todays = [r for r in self.records
                  if r["employee_id"] == emp_id and r["time"].startswith(today)]
        if not todays:
            return "Check in"
        return "Check out" if todays[-1]["type"] == "Check in" else "Check in"

    def add(self, emp_id, name, score):
        record = {
            "id": str(uuid.uuid4()),      # unique ID, so the server can ignore duplicates later
            "employee_id": emp_id,
            "name": name,
            "type": self.next_type_for(emp_id),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": round(float(score), 2),
            "synced": False,              # becomes True once the API accepts it (Step 6)
        }
        self.records.append(record)
        self.save()
        return record

    def pending(self):
        """Copies of the records that were not sent yet, oldest first."""
        return [dict(r) for r in self.records if not r["synced"]]

    def mark_synced(self, ids):
        ids = set(ids)
        for r in self.records:
            if r["id"] in ids:
                r["synced"] = True
        self.save()

    def recent(self, limit=100):
        return list(reversed(self.records[-limit:]))