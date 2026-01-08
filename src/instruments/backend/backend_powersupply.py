import ast
import json
import time
import os
import paho.mqtt.client as mqtt
import InitializeCortex
from src.instruments.hardware.dcpowersupply import PowerSupply

# --- CLASS DEFINITION ---
class BackendPowerSupply(PowerSupply):
    
    def __init__(self, ip: str, mqtt_topic: str):
        super().__init__(ip)
        self.mqtt_path = mqtt_topic
        
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def open_mqtt(self):
        # NOTE: Ensure this host is accessible from where you run the script
        self.client.connect(host="fys-s-dep-bkr01.fysad.fys.kuleuven.be")
        self.client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc, props=None):
        if rc == 0:
            client.subscribe(self.mqtt_path)
            print(f'PSU subscribed to {self.mqtt_path}')

    def on_message(self, client, userdata, message):
        payload_str = message.payload.decode()
        try:
            # Expected format: "('set', 1, 5.0)" -> mode, channel, value
            data = ast.literal_eval(payload_str)
            mode = data[0]
            channel = int(data[1])
            value = float(data[2]) if len(data) > 2 else 0.0
            
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"PSU Error: Wrong payload format: {payload_str} | {e}")
            return

        print(f"PSU Mode: {mode}, Channel: {channel}")
        
        try:
            if mode == "set":
                print(f"Setting {value}V on channel {channel}")
                self.set_voltage(channel, value)
                
            elif mode == 'enable':
                self.enable(channel)
                
            elif mode == 'disable':
                self.disable(channel)
        except Exception as e:
            print(f"PSU Hardware Error: {e}")

# --- MAIN RUNNER LOGIC ---
if __name__ == "__main__":
    # This block only runs if you execute this file directly
    # e.g., python backend_powersupply.py

    json_filename = 'config/powersupplies.json'
    
    if not os.path.exists(json_filename):
        print(f"Error: '{json_filename}' not found in the current directory.")
        exit(1)

    with open(json_filename, 'r') as f:
        try:
            psu_data_list = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            exit(1)

    active_psus = []

    print(f"Found {len(psu_data_list)} power supplies defined.")

    for entry in psu_data_list:
        try:
            psu_ip = entry['ip']
            psu_id = entry['id']
            psu_serial = entry['serialnumber']
            
            # Topic format: id/serialnumber
            mqtt_topic = f"{psu_id}/{psu_serial}"
            
            print(f"Initializing PSU ({entry['name']}) -> IP: {psu_ip}, Topic: {mqtt_topic}")
            
            psu_backend = BackendPowerSupply(psu_ip, mqtt_topic)
            psu_backend.open_mqtt()
            
            active_psus.append(psu_backend)
            
        except KeyError as e:
            print(f"Skipping entry due to missing field: {e}")
        except Exception as e:
            print(f"Failed to initialize PSU {entry.get('name', 'Unknown')}: {e}")

    print("\nAll Power Supplies are running background MQTT listeners.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
