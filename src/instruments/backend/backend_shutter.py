import threading
import ast
from typing import Any
import paho.mqtt.client as mqtt
import InitializeCortex
from src.instruments.hardware.shutter import Shutter

class BackendShutter(Shutter):

    def __init__(self, resource_string: str, device="Dev1", channel="PFI2"):
        super().__init__(device=device, channel=channel)
        self.mqtt_path = resource_string
        
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def open_mqtt(self):
        self.client.connect(host="fys-s-dep-bkr01.fysad.fys.kuleuven.be")
        self.client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc, props=None):
        if rc == 0:
            client.subscribe(self.mqtt_path)
            print(f'Shutter subscribed to {self.mqtt_path}')

    def on_message(self, client, userdata, message):
        payload_str = message.payload.decode()
        try:
            # Expected format: "('pulse', 100)" or "('open', 0)"
            mode, value = ast.literal_eval(payload_str)
            value = float(value)
        except (ValueError, SyntaxError) as e:
            print(f"Shutter Error: Wrong payload format: {payload_str} | {e}")
            return

        print(f"Shutter Mode: {mode}, Value: {value}")
        
        try:
            if mode == "open":
                self.open_shutter()
            elif mode == "close":
                self.close_shutter()
            elif mode == 'pulse':
                print(f"Pulsing shutter for {value} ms...")
                # Daemon thread ensures it doesn't block shutdown
                pulse_thread = threading.Thread(target=self.pulse, args=(value,), daemon=True)
                pulse_thread.start()
        except Exception as e:
             print(f"Shutter Hardware Error: {e}")
             
             
            
if __name__ == "__main__":
    shutter = BackendShutter(resource_string = "shutter/0000", mqtt_topic = topic)
    awg.open_mqtt()
    while True: continue
