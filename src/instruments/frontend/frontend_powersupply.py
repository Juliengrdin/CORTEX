import paho.mqtt.client as mqtt
import time

class RemotePowerSupply:
    def __init__(self, mqtt_topic: str, broker_address="fys-s-dep-bkr01.fysad.fys.kuleuven.be"):
        self.topic = mqtt_topic
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.connect(broker_address)
        self.client.loop_start()

    def set_voltage(self, channel: int, volts: float):
        """Set voltage for a specific channel."""
        # Backend expects: ('set', channel, value)
        payload = f"('set', {channel}, {volts})"
        self.client.publish(self.topic, payload)

    def enable(self, channel: int):
        """Enable specific channel."""
        # Backend expects 3 items even for enable
        payload = f"('enable', {channel}, 0)"
        self.client.publish(self.topic, payload)

    def disable(self, channel: int):
        """Disable specific channel."""
        payload = f"('disable', {channel}, 0)"
        self.client.publish(self.topic, payload)

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    psu = RemotePowerSupply("RIGOLPS/0000")
    psu.set_voltage(1, 5.0)  # Set Ch1 to 5V
    psu.enable(1)            # Turn Ch1 ON
    time.sleep(2)
    psu.disable(1)           # Turn Ch1 OFF
    psu.close()
