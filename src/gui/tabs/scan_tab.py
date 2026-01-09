from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ScanTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Scan Page (Placeholder)"))
