import sys
import time

# --- Constants & Enums ---
class CallbackAPIVersion:
    VERSION1 = 1
    VERSION2 = 2

class MQTTMessage:
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload.encode('utf-8') if isinstance(payload, str) else payload

# --- The Fake Client ---
class Client:
    def __init__(self, client_id="", clean_session=True, userdata=None, 
                 protocol=4, transport="tcp", callback_api_version=None):
        self.client_id = client_id
        self.connected = False
        self.subscriptions = []
        self.on_connect = None
        self.on_message = None

    def connect(self, host, port=1883, keepalive=60):
        print(f"[MOCK] Connecting to {host}:{port}...")
        self.connected = True
        if self.on_connect:
            self.on_connect(self, None, {}, 0, None)
        return 0

    def loop_start(self):
        print(f"[MOCK] Loop started.")

    def loop_stop(self, force=False):
        print(f"[MOCK] Loop stopped.")

    def disconnect(self):
        print(f"[MOCK] Disconnected.")
        self.connected = False

    def subscribe(self, topic, qos=0):
        print(f"[MOCK] Subscribed to '{topic}'")
        self.subscriptions.append(topic)
        return (0, 1)

    def publish(self, topic, payload=None, qos=0, retain=False):
        print(f"[MOCK] >> PUBLISH: {topic} : {payload}")
        return None 
    
    def simulate_rx(self, topic, payload_str):
        if self.on_message:
            msg = MQTTMessage(topic, payload_str)
            print(f"[MOCK] << SIMULATED RX: {topic} : {payload_str}")
            self.on_message(self, None, msg)

# ==============================================================================
# CRITICAL FIX: SELF-REFERENCE
# This tricks Python into thinking this file is 'paho', 'paho.mqtt', AND 'paho.mqtt.client'
# ==============================================================================
if "sys" in locals():
    this_module = sys.modules[__name__]
    
    # 1. Allow 'paho.mqtt' to resolve to this module
    mqtt = this_module 
    
    # 2. Allow 'paho.mqtt.client' to resolve to this module
    client = this_module
