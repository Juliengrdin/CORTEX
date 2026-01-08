import sys
import os

# Ensure the root directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow
from src.gui.builder import InstrumentPanel

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Optional: Apply Global Theme
    # app.setStyleSheet(Style.Default.light)

    win = QMainWindow()
    win.setWindowTitle("CORTEX Laboratory Dashboard")
    win.resize(960, 500)

    panel = InstrumentPanel()
    win.setCentralWidget(panel)

    win.show()
    sys.exit(app.exec())
