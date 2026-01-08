import paho.mqtt.client as mqtt
import time

class RemoteShutter:
    def __init__(self, mqtt_topic: str, broker_address="fys-s-dep-bkr01.fysad.fys.kuleuven.be"):
        self.topic = mqtt_topic
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.connect(broker_address)
        self.client.loop_start()

    def open(self):
        """Open the shutter permanently."""
        # Backend expects: ('open', value)
        payload = "('open', 0)"
        self.client.publish(self.topic, payload)

    def close_shutter(self):
        """Close the shutter immediately."""
        payload = "('close', 0)"
        self.client.publish(self.topic, payload)

    def pulse(self, duration_ms: float):
        """Pulse the shutter for X milliseconds."""
        # Backend expects: ('pulse', duration)
        payload = f"('pulse', {duration_ms})"
        self.client.publish(self.topic, payload)

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    shutter = RemoteShutter("shutter/0000")
    
    print("Pulsing for 500ms...")
    shutter.pulse(500)
    
    time.sleep(1)
    shutter.close()
