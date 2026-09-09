"""
watcher.py
----------
The pure-Python RPA piece: watches a folder for new certificate PDFs
(simulating certs landing in a shared drive / inbox attachment folder)
and automatically POSTs each new file to the FastAPI backend the moment
it appears, then moves it to /processed. No human touches this.

This is the "script-based tools to digitize operational routines" bullet,
done without any no-code tool at all. n8n (see n8n_workflow.json) does
the same job visually, so you can demo either path.

Run with:  python watcher.py
(keep uvicorn running in another terminal first)
"""

import shutil
import time
from pathlib import Path

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_DIR = Path("incoming_certificates")
PROCESSED_DIR = Path("processed")
API_URL = "http://localhost:8001/process-certificate"

WATCH_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)


class CertificateHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.lower().endswith(".pdf"):
            return
        # Give the OS a moment to finish writing the file
        time.sleep(0.5)
        self._process(Path(event.src_path))

    def _process(self, path: Path):
        print(f"[watcher] New certificate detected: {path.name}")
        try:
            with open(path, "rb") as f:
                response = requests.post(API_URL, files={"file": (path.name, f, "application/pdf")})
            response.raise_for_status()
            result = response.json()
            print(f"[watcher] Processed -> status={result['ai_status']} "
                  f"missing={result['missing_fields']} summary={result['ai_summary'][:80]}")
        except requests.RequestException as e:
            print(f"[watcher] ERROR calling API for {path.name}: {e}")
            return

        shutil.move(str(path), PROCESSED_DIR / path.name)


if __name__ == "__main__":
    handler = CertificateHandler()
    observer = Observer()
    observer.schedule(handler, str(WATCH_DIR), recursive=False)
    observer.start()
    print(f"[watcher] Watching '{WATCH_DIR}/' for new PDFs. Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
