import time
import random
import threading
import re
import paho.mqtt.client as mqtt
from collections import defaultdict

class InstrumentSimulator:
    def __init__(self, client: mqtt.Client):
        self.client = client
        self.state = {}

    def tick(self):
        """Called periodically to publish updates if needed."""
        pass

    def on_message(self, topic: str, payload: str):
        """Handle incoming commands."""
        pass


class SimulatedCamera(InstrumentSimulator):
    def __init__(self, client):
        super().__init__(client)
        self.topic = "HAMAMATSU/0000"

    def tick(self):
        # Publish random count
        count = int(random.gauss(500, 50))
        if count < 0: count = 0
        self.client.publish(self.topic, str(count))


class SimulatedWavemeter(InstrumentSimulator):
    def __init__(self, client, channels=8):
        super().__init__(client)
        self.channels = channels
        self.base_topic = "HFWM/8731"
        self.setpoints = {ch: 300.0 for ch in range(1, channels+1)}

    def tick(self):
        timestamp = time.time()
        for ch in range(1, self.channels + 1):
            # Simulate drifting around setpoint
            # Drift logic: random walk or just noise around setpoint
            noise = (random.random() - 0.5) * 0.0001
            current_freq = self.setpoints[ch] + noise

            # Format: "[timestamp, value]"
            payload = f"[{timestamp}, {current_freq:.6f}]"
            topic = f"{self.base_topic}/frequency/{ch}"
            self.client.publish(topic, payload)

    def on_message(self, topic: str, payload: str):
        # Topic format: HFWM/8731/setpoint/{ch}
        if "setpoint" in topic:
            try:
                parts = topic.split('/')
                ch = int(parts[-1])
                val = float(payload)
                self.setpoints[ch] = val
                print(f"[FakeBackend] Wavemeter Ch{ch} setpoint -> {val}")
            except Exception as e:
                print(f"[FakeBackend] Error parsing wavemeter command: {e}")


class SimulatedPowerSupply(InstrumentSimulator):
    def __init__(self, client, device_id, serial_number, channels=3):
        super().__init__(client)
        self.topic_base = f"{device_id}/{serial_number}"
        self.channels = channels
        self.voltages = {ch: 0.0 for ch in range(1, channels+1)}
        self.enabled = {ch: False for ch in range(1, channels+1)}

    def on_message(self, topic, payload):
        if topic != self.topic_base:
            return

        # Payload format: "('set', ch, val)" or "('enable', ch, 0)"
        # We need to parse this string tuple
        try:
            # Safe eval or regex
            # payload is string like "('set', 1, 5.0)"
            # Let's remove parens and split
            content = payload.strip("()").replace("'", "").split(", ")
            cmd = content[0]
            ch = int(content[1])
            val = float(content[2])

            if cmd == "set":
                self.voltages[ch] = val
                print(f"[FakeBackend] PSU {self.topic_base} Ch{ch} Set {val}V")
            elif cmd == "enable":
                self.enabled[ch] = True
                print(f"[FakeBackend] PSU {self.topic_base} Ch{ch} Enabled")
            elif cmd == "disable":
                self.enabled[ch] = False
                print(f"[FakeBackend] PSU {self.topic_base} Ch{ch} Disabled")

        except Exception as e:
            print(f"[FakeBackend] PSU Parse Error: {e} | Payload: {payload}")


class SimulatedAWG(InstrumentSimulator):
    def __init__(self, client):
        super().__init__(client)
        self.topic = "TG2511A/0000"
        self.freq = 10.0
        self.ampl = 100.0
        self.output = False

    def on_message(self, topic, payload):
        if topic != self.topic:
            return

        try:
            # Payload: "('freq', 15.5)"
            content = payload.strip("()").replace("'", "").split(", ")
            cmd = content[0]
            val = float(content[1])

            if cmd == "freq":
                self.freq = val
                print(f"[FakeBackend] AWG Freq -> {val} MHz")
            elif cmd == "ampl":
                self.ampl = val
                print(f"[FakeBackend] AWG Ampl -> {val} mV")
            elif cmd == "enable":
                self.output = True
                print("[FakeBackend] AWG Output ON")
            elif cmd == "disable":
                self.output = False
                print("[FakeBackend] AWG Output OFF")

        except Exception as e:
            print(f"[FakeBackend] AWG Parse Error: {e}")


class SimulatedShutter(InstrumentSimulator):
    def __init__(self, client):
        super().__init__(client)
        self.topic = "shutter/0000"
        self.state = "closed"

    def on_message(self, topic, payload):
        if topic != self.topic:
            return

        try:
            content = payload.strip("()").replace("'", "").split(", ")
            cmd = content[0]
            val = float(content[1]) # Duration or dummy

            if cmd == "open":
                self.state = "open"
                print("[FakeBackend] Shutter OPEN")
            elif cmd == "close":
                self.state = "closed"
                print("[FakeBackend] Shutter CLOSED")
            elif cmd == "pulse":
                print(f"[FakeBackend] Shutter PULSE {val}ms")
                # Could simulate async pulse but minimal for now

        except Exception as e:
            print(f"[FakeBackend] Shutter Parse Error: {e}")


class FakeBackend:
    def __init__(self):
        # Create a client that connects to the Mock Broker (patched in sys.modules)
        # We assume the environment is already patched or we are using mock directly.
        # But 'import paho.mqtt.client' should return the mock class if patched.
        self.client = mqtt.Client("FakeBackend")
        self.client.on_message = self.on_message

        # Connect to "localhost" (Mock ignores this)
        self.client.connect("localhost")
        self.running = False

        # Initialize Simulators
        self.simulators = []

        # 1. Camera
        self.simulators.append(SimulatedCamera(self.client))

        # 2. Wavemeter (Multi-channel)
        # Listens to HFWM/8731/setpoint/#
        wm = SimulatedWavemeter(self.client)
        self.simulators.append(wm)
        self.client.subscribe("HFWM/8731/setpoint/#")

        # 3. AWG
        awg = SimulatedAWG(self.client)
        self.simulators.append(awg)
        self.client.subscribe("TG2511A/0000")

        # 4. Power Supplies
        # Config matches powersupplylist.json created earlier
        psus = [
            ("RIGOLPS", "0000"),
            ("RIGOLPS", "0001"),
            ("RIGOLPS", "0002"),
            ("UNITYPS", "0003")
        ]
        for pid, sn in psus:
            psu = SimulatedPowerSupply(self.client, pid, sn)
            self.simulators.append(psu)
            self.client.subscribe(f"{pid}/{sn}")

        # 5. Shutter
        shutter = SimulatedShutter(self.client)
        self.simulators.append(shutter)
        self.client.subscribe("shutter/0000")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload
        if isinstance(payload, bytes):
            payload = payload.decode()

        # Route to simulators
        for sim in self.simulators:
            sim.on_message(topic, payload)

    def run(self):
        self.running = True
        print(">> [FakeBackend] Started. Simulating devices...")
        self.client.loop_start()

        while self.running:
            for sim in self.simulators:
                sim.tick()
            time.sleep(1.0) # Global tick rate

    def stop(self):
        self.running = False
        self.client.loop_stop()
        print(">> [FakeBackend] Stopped.")
