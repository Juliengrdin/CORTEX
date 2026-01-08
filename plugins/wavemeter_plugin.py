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
    def __init__(self, num_channels=8):
        # Initialize with 8 channels by default, or configurable
        super().__init__()
        self.num_channels = num_channels
        self.channels = {}  # Map channel ID to widget

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Title
        title = QLabel("HighFinesse Multi-Channel Wavemeter")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)

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
        # Subscribe to all wavemeter channels using the existing format + wildcard
        # Existing format: HFWM/8731/frequency/1
        # Wildcard: HFWM/+/frequency/+
        # Assuming '8731' is the serial number, we might want to catch all wavemeters or a specific one.
        # Let's use wildcard for serial number too if we want to be generic, or just subscribe to this specific pattern.
        # "HFWM/+/frequency/+" covers any serial number and any channel.
        return ["HFWM/+/frequency/+"]

    def handle_message(self, topic, payload):
        # Expected topic: HFWM/<serial>/frequency/<channel>
        # Payload format: "(timestamp, value)" string, e.g. "(123456.789, 300.1234)"

        try:
            parts = topic.split('/')
            # Check format: HFWM / Serial / frequency / Channel
            if len(parts) == 4 and parts[0] == "HFWM" and parts[2] == "frequency":
                channel_id = int(parts[3])

                # Parse payload
                # Remove parens if present and split
                clean_payload = payload.strip("()")
                # The existing code used: timestamp, value = [float(f) for f in message.payload.decode()[1:-1].split(", ")]
                # So it expects "(ts, val)"

                # Check if payload is wrapped in parens
                if payload.startswith("(") and payload.endswith(")"):
                    content = payload[1:-1]
                    ts_str, val_str = content.split(",")
                    frequency = float(val_str)
                else:
                    # Maybe it's just the value? Fallback
                    frequency = float(payload)

                # Ensure we have a widget for this channel
                if channel_id in self.channels:
                    self.channels[channel_id].update_frequency(frequency)
                else:
                    # Optional: Dynamically add channel if it doesn't exist?
                    # For now, we initialized N channels.
                    pass

        except ValueError:
            pass  # Handle parse error
        except Exception as e:
            print(f"Wavemeter Plugin Error: {e}")
