import paho.mqtt.client as mqtt
import time

class RemoteAWG:
    def __init__(self, mqtt_topic: str, broker_address="fys-s-dep-bkr01.fysad.fys.kuleuven.be"):
        self.topic = mqtt_topic
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.connect(broker_address)
        self.client.loop_start()

    def set_frequency(self, mhz: float):
        """Sets frequency in MHz."""
        # Backend expects: ('freq', value)
        payload = f"('freq', {mhz})"
        print("FRONTEND AWG TRIGGERED frequency")
        self.client.publish(self.topic, payload)

    def set_amplitude(self, mv: float):
        """Sets amplitude in mV."""
        # Backend expects: ('ampl', value)
        payload = f"('ampl', {mv})"
        self.client.publish(self.topic, payload)

    def enable(self):
        """Turns output ON."""
        payload = "('enable', 0)"
        print("FRONTEND AWG TRIGGERED")
        self.client.publish(self.topic, payload)

    def disable(self):
        """Turns output OFF."""
        payload = "('disable', 0)"
        self.client.publish(self.topic, payload)

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()

# Usage Example
if __name__ == "__main__":
    awg = RemoteAWG("TG2511A/0000")
    awg.set_frequency(15.5) # 15.5 MHz
    awg.set_amplitude(500)  # 500 mV
    awg.enable()
    time.sleep(1)
    awg.close()
