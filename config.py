import threading
from pathlib import Path
from browser_use import Controller

# Paths
TEMPLATE_PATH = "Template.xlsx"
JDS_PATH = Path("JDs")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Browser-Use controller
controller = Controller()

# Thread-safe status tracker for UI
class SharedStatus:
    def __init__(self):
        self._value = "Idle"
        self._lock = threading.Lock()

    def set(self, val: str):
        with self._lock:
            self._value = val

    def get(self) -> str:
        with self._lock:
            return self._value

shared_status = SharedStatus()

# 🔐 Track the selected JD filename safely across threads
CURRENT_SELECTED_JD = None

def set_selected_jd(filename: str):
    global CURRENT_SELECTED_JD
    CURRENT_SELECTED_JD = filename

def get_selected_jd() -> str:
    return CURRENT_SELECTED_JD