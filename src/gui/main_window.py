import sys
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QListWidget,
    QStackedWidget,
)

from src.gui.assets.csstyle import Style
from src.gui.tabs.devices_tab import InstrumentPanel
from src.gui.tabs.live_update_tab import LiveUpdateWidget
from src.gui.tabs.scan_tab import ScanTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CORTEX Laboratory Dashboard")
        self.resize(1200, 800)

        # Main Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Navigation
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150) # Fixed width of 150px as requested
        self.sidebar.setStyleSheet(Style.List.light)
        self.sidebar.addItem("Devices")
        self.sidebar.addItem("Live Update")
        self.sidebar.addItem("Scan")
        self.sidebar.setCurrentRow(0)
        self.sidebar.currentRowChanged.connect(self.display_page)
        main_layout.addWidget(self.sidebar)

        # 2. Content Stack
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)

        # --- Page 1: Devices (Principal) ---
        self.devices_panel = InstrumentPanel()
        self.stack.addWidget(self.devices_panel)

        # --- Page 2: Live Update ---
        # We pass the loaded instruments to the LiveUpdateWidget
        self.live_update_page = LiveUpdateWidget(self.devices_panel.loaded_instruments)
        self.stack.addWidget(self.live_update_page)

        # --- Page 3: Scan ---
        self.scan_page = ScanTab()
        self.stack.addWidget(self.scan_page)

    def display_page(self, index):
        self.stack.setCurrentIndex(index)
