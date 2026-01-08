import sys
import os
import InitializeCortex
from src.gui.assets.instrument_base import InstrumentBase, Parameter
from src.instruments.frontend.frontend_awg import RemoteAWG

# ==============================================================================
#   SECTION 1: USER CONFIGURATION
#   (Edit these values to change instrument settings, labels, or connection)
# ==============================================================================

# GUI Display Name
DISPLAY_NAME = "AWG TG2511A"

# Connection Settings
MQTT_BROKER  = "fys-s-dep-bkr01.fysad.fys.kuleuven.be"
MQTT_TOPIC   = "TG2511A/0000"

# Parameter Configuration
# You can adjust labels, units, and scannability here.
# Note: Do not change the dictionary keys (e.g., "freq_config"), just the values.
CONFIG = {
    "output": {
        "label": "Output Enabled",
        "type":  "bool",
        "scan":  False
    },
    "frequency": {
        "label": "Frequency",
        "unit":  "MHz",
        "type":  "float",
        "scan":  True
    },
    "amplitude": {
        "label": "Amplitude",
        "unit":  "mV",
        "type":  "float",
        "scan":  True
    }
}

# ==============================================================================
#   SECTION 2: INSTRUMENT LOGIC
#   (Logic handles the mapping between the Config above and the Driver)
# ==============================================================================

class MqttAWG(InstrumentBase):
    def __init__(self):
        super().__init__(DISPLAY_NAME)
        self.driver = None
        self.category = "Miscellaneous"

        # --- 1. Output Enable ---
        cfg = CONFIG["output"]
        self.add_parameter(Parameter(
            name="output",
            label=cfg["label"],
            param_type=cfg["type"],
            set_cmd=self.set_output_state,
            scannable=cfg["scan"]
        ))

        # --- 2. Frequency ---
        cfg = CONFIG["frequency"]
        self.add_parameter(Parameter(
            name="frequency",
            label=cfg["label"],
            param_type=cfg["type"],
            unit=cfg["unit"],
            set_cmd=self.set_freq_wrapper,
            scannable=cfg["scan"]
        ))

        # --- 3. Amplitude ---
        cfg = CONFIG["amplitude"]
        self.add_parameter(Parameter(
            name="amplitude",
            label=cfg["label"],
            param_type=cfg["type"],
            unit=cfg["unit"],
            set_cmd=self.set_amp_wrapper,
            scannable=cfg["scan"]
        ))
    
        self.connect_instrument()

    def connect_instrument(self):
        print(f"[{self.name}] Connecting to {MQTT_BROKER} on topic {MQTT_TOPIC}...")
        try:
            # We use the global configuration variables here
            self.driver = RemoteAWG(MQTT_TOPIC, broker_address=MQTT_BROKER)
            print(f"[{self.name}] Connected successfully.")
        except Exception as e:
            print(f"[{self.name}] Connection failed: {e}")

    # --- Wrapper functions (Logic) ---

    def set_output_state(self, is_on: bool):
        if self.driver:
            print(is_on)
            if is_on:
                self.driver.enable()
            else:
                self.driver.disable()

    def set_freq_wrapper(self, value):
        if self.driver:
            self.driver.set_frequency(float(value))

    def set_amp_wrapper(self, value):
        if self.driver:
            self.driver.set_amplitude(float(value))
