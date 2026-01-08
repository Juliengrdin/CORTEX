from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QScrollArea, QFrame)
from PyQt6.QtCore import pyqtSlot, Qt
from src.core.plugin_interface import InstrumentPlugin
import json

class ChannelWidget(QGroupBox):
    def __init__(self, channel_id):
        super().__init__(f"Channel {channel_id}")
        self.channel_id = channel_id
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Frequency Display
        self.freq_label = QLabel("Waiting for data...")
        self.freq_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        self.freq_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.freq_label)

    def update_frequency(self, frequency):
        self.freq_label.setText(f"{frequency:.6f} THz")

class WavemeterPlugin(InstrumentPlugin):
    def __init__(self, num_channels=4):
        super().__init__()
        self.num_channels = num_channels
        self.channels = {}  # Map channel ID to widget

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Scroll Area for many channels
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        self.grid_layout = QVBoxLayout(content_widget)

        # Create Channel Widgets
        for i in range(1, self.num_channels + 1):
            channel_widget = ChannelWidget(i)
            self.channels[i] = channel_widget
            self.grid_layout.addWidget(channel_widget)

        self.grid_layout.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def get_subscribe_topics(self) -> list[str]:
        # Subscribe to all wavemeter channels
        # Topic format: instruments/wavemeter/channel/+/frequency
        return ["instruments/wavemeter/channel/+/frequency"]

    def handle_message(self, topic, payload):
        # Expected topic: instruments/wavemeter/channel/<id>/frequency
        # Payload: frequency value (float or string)

        try:
            parts = topic.split('/')
            if len(parts) >= 4 and parts[1] == "wavemeter" and parts[2] == "channel":
                channel_id = int(parts[3])
                frequency = float(payload)

                if channel_id in self.channels:
                    self.channels[channel_id].update_frequency(frequency)
        except ValueError:
            pass  # Handle parse error
        except Exception as e:
            print(f"Wavemeter Plugin Error: {e}")
