import sys
import os
import time
import random
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force Mock Environment
import tests.mock_paho_mqtt_plugin as mock_mqtt
sys.modules["paho"] = mock_mqtt
sys.modules["paho.mqtt"] = mock_mqtt
sys.modules["paho.mqtt.client"] = mock_mqtt

from src.gui.builder import InstrumentPanel

class BackendSimulator:
    def __init__(self):
        self.client = mock_mqtt.Client("BackendSimulator")
        self.client.on_message = self.on_message
        self.client.connect("localhost")
        self.running = True

        # Subscribe to setpoints
        self.client.subscribe("HFWM/8731/setpoint/#")

    def on_message(self, client, userdata, msg):
        print(f"[{'BACKEND'}] Received Command: {msg.topic} -> {msg.payload}")

    def run(self):
        print("[BACKEND] Simulator started...")
        while self.running:
            try:
                # 1. Publish Wavemeter Data (Channels 1-8)
                timestamp = time.time()
                for ch in range(1, 9):
                    # Random freq around 300 THz
                    val = 300.0 + random.random()
                    payload = f"[{timestamp}, {val:.6f}]"
                    topic = f"HFWM/8731/frequency/{ch}"
                    self.client.publish(topic, payload)

                # 2. Publish Camera Data
                count = int(random.random() * 1000)
                self.client.publish("HAMAMATSU/0000", str(count))

                time.sleep(1.0) # Update every second
            except Exception as e:
                print(f"[BACKEND] Error: {e}")

    def stop(self):
        self.running = False


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. Start GUI
    win = QMainWindow()
    win.setWindowTitle("CORTEX Lab Dashboard (TEST MODE)")
    win.resize(1200, 600)
    panel = InstrumentPanel()
    win.setCentralWidget(panel)
    win.show()

    # 2. Start Backend Simulator in background thread
    backend = BackendSimulator()
    t = threading.Thread(target=backend.run, daemon=True)
    t.start()

    print(">> Launching GUI with Fake Backend...")
    try:
        sys.exit(app.exec())
    finally:
        backend.stop()
