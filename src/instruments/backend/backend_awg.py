import ast
from typing import Any
import paho.mqtt.client as mqtt
import InitializeCortex
from src.instruments.hardware.awg import TG2511A

topic = 'TG2511A/0000'

class BackendAWG(TG2511A):

    def __init__(self, resource_string: str, mqtt_topic: str):
        super().__init__(resource_string)
        self.mqtt_path = mqtt_topic
        
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def open_mqtt(self):
        # Renamed to avoid confusion with hardware open() if it exists
        self.client.connect(host="fys-s-dep-bkr01.fysad.fys.kuleuven.be")
        self.client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc, props=None):
        if rc == 0:
            client.subscribe(self.mqtt_path)
            print(f'AWG subscribed to {self.mqtt_path}')

    def on_message(self, client, userdata, message):
        payload_str = message.payload.decode()
        try:
            # Expected format: "('mode', value)"
            mode, value = ast.literal_eval(payload_str)
            value = float(value)
        except (ValueError, SyntaxError) as e:
            print(f"AWG Error: Wrong payload format: {payload_str} | {e}")
            return

        print(f"AWG Mode: {mode}, Value: {value}")
        
        try:
            if mode == "enable":
                self.output_on()
            elif mode == "disable":
                self.output_off()
            elif mode == 'ampl':
                # FIX: Convert mV to Volts (divide by 1000), not multiply
                print(f"Setting amplitude: {value} mV")
                self.set_amplitude(value * 1e-3)
            elif mode == 'freq':
                # Convert MHz to Hz
                print(f"Setting frequency: {value} MHz")
                self.set_frequency(value * 1e6)
        except Exception as e:
            print(f"AWG Hardware Error: {e}")
            
            
if __name__ == "__main__":
    awg = BackendAWG(resource_string = AWG_RESSOURCE, mqtt_topic = topic)
    awg.open_mqtt()
    while True: continue
