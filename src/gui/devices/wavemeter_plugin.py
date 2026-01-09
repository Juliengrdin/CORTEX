import sys
import os
import InitializeCortex
from src.gui.assets.instrument_base import InstrumentBase, Parameter
from src.instruments.frontend.frontend_wavemeter import MqttWavemeter
from functools import partial
from PyQt6.QtCore import pyqtSlot

# ==============================================================================
#   SECTION 1: USER CONFIGURATION
# ==============================================================================
DISPLAY_NAME = "HighFinesse Wavemeter (Multi-Channel)"
CATEGORY = 'Sensor'
RESOURCE_BASE  = "HFWM/8731/frequency/"

# ==============================================================================
#   SECTION 2: INSTRUMENT LOGIC
# ==============================================================================
class WavemeterPlugin(InstrumentBase):
    def __init__(self):
        super().__init__(DISPLAY_NAME)
        self.drivers = {}
        self.category = CATEGORY

        # Define 8 channels
        for ch in range(1, 9):
            self.add_channel_parameters(ch)

        self.connect_instrument()

    def add_channel_parameters(self, channel):
        # Frequency Readout
        self.add_parameter(Parameter(
            name=f"frequency_ch{channel}",
            label=f"Ch {channel} Freq",
            param_type='input',
            unit="THz",
            set_cmd=None,
            get_cmd=partial(self.get_freq_wrapper, channel),
            scannable=False
        ))

        # Setpoint Input
        self.add_parameter(Parameter(
            name=f"setpoint_ch{channel}",
            label=f"Ch {channel} Setpoint",
            param_type='float', # Generates a QLineEdit
            unit="THz",
            set_cmd=partial(self.set_setpoint_wrapper, channel),
            get_cmd=None,
            scannable=True
        ))

    def connect_instrument(self):
        for ch in range(1, 9):
            resource_id = f"{RESOURCE_BASE}{ch}"
            print(f"[{self.name}] Subscribing to {resource_id}...")
            try:
                driver = MqttWavemeter(resource_id)
                driver.open()
                self.drivers[ch] = driver

                # Connect Signal
                # using partial to pass the channel number
                driver.frequency_updated.connect(partial(self.on_freq_update, channel=ch))

            except Exception as e:
                print(f"[{self.name}] Connection failed for Ch {ch}: {e}")

    def get_freq_wrapper(self, channel):
        if channel in self.drivers:
            val = self.drivers[channel].getdata()
            return f"{val:.6f}"
        return "0.0"

    def set_setpoint_wrapper(self, channel, value):
        if channel in self.drivers:
            self.drivers[channel].set_setpoint(value)
        else:
            print(f"[{self.name}] Error: No driver for Ch {channel}")

    @pyqtSlot(float) # Slot to handle updates from background thread
    def on_freq_update(self, value, channel=None):
        # Note: partial passes channel as keyword argument if defined like that
        # logic to update the specific parameter widget
        param_name = f"frequency_ch{channel}"
        if param_name in self.parameters:
            param = self.parameters[param_name]
            if param.update_widget:
                text = f"{value:.6f}"
                param.update_widget(text)
