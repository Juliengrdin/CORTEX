import json
import sys, os
import InitializeCortex
from src.gui.assets.instrument_base import InstrumentBase, Parameter
from src.instruments.frontend.frontend_powersupply import RemotePowerSupply

# ==============================================================================
#   SECTION 1: LOAD CONFIGURATION
# ==============================================================================

# Path to your JSON file
JSON_FILE = 'config/powersupplylist.json'

# Default Settings for all Power Supplies
MQTT_BROKER = "fys-s-dep-bkr01.fysad.fys.kuleuven.be"
ACTIVE_CHANNELS = [1, 2, 3] # Channels to create widgets for

def load_psu_config():
    if not os.path.exists(JSON_FILE):
        print(f"Error: Could not find {JSON_FILE}")
        return []
    with open(JSON_FILE, 'r') as f:
        return json.load(f)

# ==============================================================================
#   SECTION 2: DYNAMIC CLASS FACTORY
# ==============================================================================

def create_psu_class(device_config):
    """
    Creates a unique class for a specific power supply based on JSON data.
    """
    
    # Extract details from JSON
    dev_name = device_config.get("name", "Unknown PSU")
    dev_id   = device_config.get("id", "RIGOLPS")
    dev_sn   = device_config.get("serialnumber", "0000")
    
    # Construct Topic: e.g., "RIGOLPS/0000"
    topic = f"{dev_id}/{dev_sn}"

    # Define the class logic (Closure)
    class DynamicPSU(InstrumentBase):
        def __init__(self):
            # The name passed here becomes the Frame Title in the GUI
            super().__init__(dev_name) 
            self.driver = None
            self.topic = topic
            self.category = 'Power Supply'

            # Create widgets for channels 1, 2, 3
            for ch in ACTIVE_CHANNELS:
                self._add_channel_params(ch)
            self.connect_instrument()

        def _add_channel_params(self, ch_num):
            # Voltage (Float)
            self.add_parameter(Parameter(
                name=f"ch{ch_num}_volt",
                label=f"Ch{ch_num} Set (V)",
                param_type="float",
                unit="V",
                set_cmd=lambda val, c=ch_num: self.set_volts_wrapper(c, val)
            ))

            # Enable (Checkbox)
            self.add_parameter(Parameter(
                name=f"ch{ch_num}_enable",
                label=f"Ch{ch_num} On/Off",
                param_type="bool",
                set_cmd=lambda val, c=ch_num: self.set_enable_wrapper(c, val)
            ))
        
        def connect_instrument(self):
            print(f"[{self.name}] Connecting to {self.topic}...")
            try:
                self.driver = RemotePowerSupply(self.topic, broker_address=MQTT_BROKER)
            except Exception as e:
                print(f"[{self.name}] Connection failed: {e}")

        # --- Wrappers ---
        def set_volts_wrapper(self, channel, volts):
            if self.driver:
                self.driver.set_voltage(channel, float(volts))

        def set_enable_wrapper(self, channel, is_on):
            if self.driver:
                if is_on: self.driver.enable(channel)
                else:     self.driver.disable(channel)

    # Return the newly created class
    return DynamicPSU

# ==============================================================================
#   SECTION 3: REGISTER CLASSES FOR MAIN.PY
# ==============================================================================

# 1. Load the list from JSON
psu_list = load_psu_config()

# 2. Loop through and create a class for each PSU
# We must assign them to global variables so 'main.py' finds them in dir(module)
for i, psu_data in enumerate(psu_list):
    # Create the class
    NewClass = create_psu_class(psu_data)
    
    # Give it a unique name in the module scope (e.g., PSU_0, PSU_1)
    # This is the "Magic" that lets main.py see them as separate plugins.
    vars()[f"PSU_{i}_{psu_data['id']}"] = NewClass
del NewClass
