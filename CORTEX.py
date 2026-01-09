import sys
import os

# Ensure the root directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
# Ensure builder environment setup is run if needed, or moved.
# Since configure_mqtt_environment was in builder.py, we should import it from devices_tab
# or ensure it runs.
# Checking src/gui/tabs/devices_tab.py, I did NOT copy the `configure_mqtt_environment` call.
# I need to verify if I copied it.
from src.gui.tabs.devices_tab import configure_mqtt_environment

if __name__ == "__main__":
    configure_mqtt_environment()

    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())
