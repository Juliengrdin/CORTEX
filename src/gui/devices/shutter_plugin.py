import sys, os
import InitializeCortex
from src.gui.assets.instrument_base import InstrumentBase, Parameter
from src.instruments.frontend.frontend_shutter import RemoteShutter

# ==============================================================================
#   SECTION 1: USER CONFIGURATION
# ==============================================================================
DISPLAY_NAME = "Ionisation Lasers Shutter"
MQTT_BROKER  = "fys-s-dep-bkr01.fysad.fys.kuleuven.be"
MQTT_TOPIC   = "shutter/0000"

CONFIG = {
    "state": {
        "label": "Shutter Open",
        "type":  "bool",
        "scan":  False  # Usually we don't scan the shutter open/close state
    },
    "pulse": {
        "label": "Pulse Duration",
        "unit":  "ms",
        "type":  "float",
        "scan":  False  # Scanning pulse duration is rare, but possible
    }
}

# ==============================================================================
#   SECTION 2: INSTRUMENT LOGIC
# ==============================================================================
class ShutterPlugin(InstrumentBase):
    def __init__(self):
        super().__init__(DISPLAY_NAME)
        self.driver = None
        self.category = 'Miscellaneous'

        # --- 1. Main Shutter State (Switch) ---
        cfg = CONFIG["state"]
        self.add_parameter(Parameter(
            name="state",
            label=cfg["label"],
            param_type=cfg["type"],
            set_cmd=self.set_state_wrapper,
            scannable=cfg["scan"]
        ))

        # --- 2. Pulse Trigger (Value + Set Button) ---
        # Clicking "Set" on this parameter will fire the pulse
        cfg = CONFIG["pulse"]
        self.add_parameter(Parameter(
            name="pulse",
            label=cfg["label"],
            param_type=cfg["type"],
            unit=cfg["unit"],
            set_cmd=self.pulse_wrapper,
            scannable=cfg["scan"]
        ))
        
        self.connect_instrument()

    def connect_instrument(self):
        print(f"[{self.name}] Connecting to {MQTT_BROKER}...")
        try:
            self.driver = RemoteShutter(MQTT_TOPIC, broker_address=MQTT_BROKER)
        except Exception as e:
            print(f"[{self.name}] Connection failed: {e}")

    def set_state_wrapper(self, is_open: bool):
        if self.driver:
            if is_open:
                self.driver.open()
            else:
                self.driver.close_shutter()

    def pulse_wrapper(self, duration_ms):
        if self.driver:
            self.driver.pulse(float(duration_ms))
            print(f"[{self.name}] Pulsed for {duration_ms}ms")
