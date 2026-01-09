import sys
import os
import threading
from PyQt6.QtWidgets import QApplication

import InitializeCortex

# Import Backend Simulator
from src.instruments.backend.fake_backend import FakeBackend

# Import GUI
# Note: configure_mqtt_environment() is called in CORTEX.py or devices_tab.py
# We should ensure the environment is configured BEFORE MainWindow is imported or initialized if possible,
# or ensure MainWindow triggers it.
# MainWindow imports devices_tab which contains the function but doesn't call it at module level (it was removed from module level call in my previous turn? No, I put it back in the file but didn't call it at module level, I called it in `if __name__ == "__main__"` of CORTEX.py).
# So we must call it here.

from src.gui.tabs.devices_tab import configure_mqtt_environment
configure_mqtt_environment()

from src.gui.main_window import MainWindow

def run_app():
    app = QApplication(sys.argv)

    # 1. Start Backend Simulator
    backend = FakeBackend()
    t = threading.Thread(target=backend.run, daemon=True)
    t.start()
    print(">> [Launcher] Fake Backend Started.")

    # 2. Start GUI
    win = MainWindow()
    win.setWindowTitle("CORTEX (Fake Backend Mode)")
    win.show()

    print(">> [Launcher] GUI Started.")
    try:
        sys.exit(app.exec())
    finally:
        backend.stop()

if __name__ == "__main__":
    run_app()
