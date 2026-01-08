import sys
import os
import InitializeCortex
from src.gui.assets.instrument_base import InstrumentBase, Parameter
from src.instruments.frontend.frontend_wavemeter import MqttWavemeter

# ==============================================================================
#   SECTION 1: USER CONFIGURATION
# ==============================================================================
DISPLAY_NAME = "HighFinesse Wavemeter NM Channel 1"
CATEGORY = 'Sensor'
RESOURCE_ID  = "HFWM/8731/frequency/1" # acts as the topic for this driver

CONFIG = {
    "frequency": {
        "label": None,
        "unit":  "THz",
        "type":  'input', # Display as string to avoid formatting issues
        "scan":  False,  # You don't 'set' this during a scan, you 'read' it
    },
    "setpoint": {
        "label": "Setpoint Frequency",
        "unit":  "THz",
        "type":  "str", # Display as string to avoid formatting issues
        "scan":  True  # You don't 'set' this during a scan, you 'read' it
    }
}

# ==============================================================================
#   SECTION 2: INSTRUMENT LOGIC
# ==============================================================================
class WavemeterPlugin(InstrumentBase):
    def __init__(self):
        super().__init__(DISPLAY_NAME)
        self.driver = None
        self.category = CATEGORY

        cfg = CONFIG["frequency"]
        self.add_parameter(Parameter(
            name="frequency",
            label=cfg["label"],
            param_type=cfg["type"],
            unit=cfg["unit"],
            set_cmd=None, # Read-only: No set command
            get_cmd=self.get_freq_wrapper,
            scannable=cfg["scan"]
        ))
        
        cfg = CONFIG["setpoint"]
        self.add_parameter(Parameter(
            name="setpoint",
            label=cfg["label"],
            param_type=cfg["type"],
            unit=cfg["unit"],
            set_cmd=None, # Read-only: No set command
            get_cmd=self.get_freq_wrapper,
            scannable=cfg["scan"]
        ))
        
        self.connect_instrument()

    def connect_instrument(self):
        print(f"[{self.name}] Subscribing to {RESOURCE_ID}...")
        try:
            # Note: The original driver expects 'resource_string'
            self.driver = MqttWavemeter(RESOURCE_ID)
            self.driver.open() # Starts the MQTT loop
        except Exception as e:
            print(f"[{self.name}] Connection failed: {e}")

    def get_freq_wrapper(self):
        if self.driver:
            val = self.driver.getdata()
            return f"{val:.6f}" # Format as string
        return "0.0"
