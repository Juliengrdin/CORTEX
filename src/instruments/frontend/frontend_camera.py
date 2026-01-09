from typing import Any
import paho.mqtt.client as mqtt
from PyQt6.QtCore import QObject, pyqtSignal

class MqttCamera(QObject):
    count_updated = pyqtSignal(int)

    client = None
    mqtt_path = ''

    def __init__(self, resource_string: str):
        super().__init__()
        self.mqtt_path = resource_string
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def open(self):
        self.client.connect(host="fys-s-dep-bkr01.fysad.fys.kuleuven.be")
        self.client.loop_start()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc, bla):
        client.subscribe(self.mqtt_path)
        print('subscribed to ' + str(self.mqtt_path))

    def on_message(self, client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage):
        try:
            payload = message.payload.decode()
            # Assuming payload is just a number (int or float)
            value = int(float(payload))
            self.count_updated.emit(value)
        except Exception as e:
            print(f"Error parsing MQTT message for Camera: {e}")

    def getdata(self):
        return 0
