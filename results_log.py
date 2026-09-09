"""
results_log.py
---------------
Lightweight structured logging infrastructure for the automation pipeline.
Every processed document gets appended as one JSON record. This keeps a
full audit trail (input file, extracted fields, AI validation result,
timing) without needing a real database for a demo/portfolio project.
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime, timezone


class Timer:
    """Simple context-manager timer, e.g.:
        with Timer() as t:
            do_work()
        print(t.elapsed_seconds)
    """
    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_seconds = round(time.perf_counter() - self._start, 3)


class ResultsLog:
    """Append-only JSON log of processed documents. Thread-safe enough
    for a single-process FastAPI dev server + a watchdog script."""

    def __init__(self, path: str = "processed/results_log.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _read_all(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def add(self, record: dict) -> dict:
        record.setdefault("logged_at", datetime.now(timezone.utc).isoformat())
        with self._lock:
            records = self._read_all()
            record["id"] = len(records) + 1
            records.append(record)
            self.path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        return record

    def all(self):
        with self._lock:
            return self._read_all()

    def get(self, record_id: int):
        for r in self.all():
            if r["id"] == record_id:
                return r
        return None
