import sys
import time
import fnmatch
from collections import defaultdict

# --- Constants & Enums ---
class CallbackAPIVersion:
    VERSION1 = 1
    VERSION2 = 2

class MQTTMessage:
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload.encode('utf-8') if isinstance(payload, str) else payload

# --- Mock Broker Singleton ---
class MockBroker:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MockBroker, cls).__new__(cls)
            cls._instance.subscribers = defaultdict(list)
        return cls._instance

    def subscribe(self, topic, client):
        self.subscribers[topic].append(client)

    def unsubscribe(self, topic, client):
        if topic in self.subscribers:
            if client in self.subscribers[topic]:
                self.subscribers[topic].remove(client)

    def publish(self, topic, payload):
        # Very basic matching: Direct match or simple wildcard handling could be added
        # iterating a copy to avoid modification during iteration issues
        for sub_topic, clients in list(self.subscribers.items()):
            # Check for match (using fnmatch for simple wildcard support like # or +)
            # MQTT wildcards are specific, but fnmatch is a decent approx for a mock
            # Mapping MQTT wildcards to fnmatch: + -> *, # -> * (roughly)
            # A proper MQTT matcher is complex, we will support direct match and simple # at end

            match = False
            if sub_topic == topic:
                match = True
            elif sub_topic.endswith('#') and topic.startswith(sub_topic[:-1]):
                match = True

            if match:
                msg = MQTTMessage(topic, payload)
                for client in clients:
                    if client.on_message:
                        try:
                            client.on_message(client, None, msg)
                        except Exception as e:
                            print(f"[MOCK BROKER] Error delivering message to client: {e}")

# --- The Fake Client ---
class Client:
    def __init__(self, client_id="", clean_session=True, userdata=None, 
                 protocol=4, transport="tcp", callback_api_version=None):
        self.client_id = client_id
        self.connected = False
        self.subscriptions = []
        self.on_connect = None
        self.on_message = None
        self.broker = MockBroker()

    def connect(self, host, port=1883, keepalive=60):
        print(f"[MOCK] Connecting to {host}:{port}...")
        self.connected = True
        if self.on_connect:
            self.on_connect(self, None, {}, 0, None)
        return 0

    def loop_start(self):
        # print(f"[MOCK] Loop started.")
        pass

    def loop_stop(self, force=False):
        # print(f"[MOCK] Loop stopped.")
        pass

    def disconnect(self):
        print(f"[MOCK] Disconnected.")
        self.connected = False

    def subscribe(self, topic, qos=0):
        print(f"[MOCK] Subscribed to '{topic}'")
        self.subscriptions.append(topic)
        self.broker.subscribe(topic, self)
        return (0, 1)

    def publish(self, topic, payload=None, qos=0, retain=False):
        # print(f"[MOCK] >> PUBLISH: {topic} : {payload}")
        self.broker.publish(topic, payload)
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
