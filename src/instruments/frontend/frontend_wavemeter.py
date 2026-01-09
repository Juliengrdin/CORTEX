from typing import Any
import paho.mqtt.client as mqtt
from PyQt6.QtCore import QObject, pyqtSignal

class MqttWavemeter(QObject):
    frequency_updated = pyqtSignal(float)

    wavelength_value = 0.0
    client = None
    mqtt_path = ''


    def __init__(self, resource_string: str):
        super().__init__()
        self.mqtt_path = resource_string
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def open(self):
        # Using a dummy host for now as per original code, or localhost if testing
        self.client.connect(host="fys-s-dep-bkr01.fysad.fys.kuleuven.be")
        self.client.loop_start()

    def on_connect(self,client: mqtt.Client, userdata, flags, rc, bla):
        client.subscribe(self.mqtt_path)
        print('subscribed to '+str(self.mqtt_path))

    def on_message(self,client: mqtt.Client,userdata: Any,message: mqtt.MQTTMessage,):
        try:
            # Payload format expected: "[timestamp, value]"
            payload = message.payload.decode()
            # Remove brackets and split
            parts = payload.strip("[]").split(", ")
            if len(parts) >= 2:
                timestamp = float(parts[0])
                value = float(parts[1])

                if value > 0:
                    self.frequency_value = value
                    self.frequency_updated.emit(value)
        except Exception as e:
            print(f"Error parsing MQTT message: {e}")


    def getdata(self):
        return getattr(self, 'frequency_value', 0.0)

    def set_setpoint(self, value: float):
        # Deducing setpoint topic: HFWM/8731/frequency/X -> HFWM/8731/setpoint/X
        topic = self.mqtt_path.replace("frequency", "setpoint")
        print(f"[{self.mqtt_path}] Publishing setpoint {value} to {topic}")
        self.client.publish(topic, str(value))


if __name__ == "__main__":
    # For testing only
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    wm = MqttWavemeter('HFWM/8731/frequency/1')
    wm.open()

    wm.frequency_updated.connect(lambda f: print(f"Signal received: {f}"))

    sys.exit(app.exec())
