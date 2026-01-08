from PyQt6.QtCore import QObject, QThread, pyqtSignal
import paho.mqtt.client as mqtt

class MqttManager(QThread):
    """
    Manages MQTT connection and message handling in a separate thread.
    Emits signals when messages are received.
    """
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    message_received = pyqtSignal(str, str)  # topic, payload

    def __init__(self, broker_address="localhost", port=1883, keepalive=60):
        super().__init__()
        self.broker_address = broker_address
        self.port = port
        self.keepalive = keepalive
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.running = False
        self.subscriptions = []

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Connected to MQTT Broker")
            self.connected.emit()
            # Resubscribe if we have pending subscriptions
            for topic in self.subscriptions:
                self.client.subscribe(topic)
                print(f"Subscribed to: {topic}")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, flags, rc, properties=None):
        print("Disconnected from MQTT Broker")
        self.disconnected.emit()

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            self.message_received.emit(msg.topic, payload)
        except Exception as e:
            print(f"Error processing message: {e}")

    def subscribe(self, topic):
        if topic not in self.subscriptions:
            self.subscriptions.append(topic)
            if self.client.is_connected():
                self.client.subscribe(topic)
                print(f"Subscribed to: {topic}")

    def run(self):
        self.running = True
        try:
            self.client.connect(self.broker_address, self.port, self.keepalive)
            self.client.loop_start()

            # Keep the thread alive
            while self.running:
                self.msleep(100)

        except Exception as e:
            print(f"MQTT Connection Error: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

    def stop(self):
        self.running = False
        self.wait()
