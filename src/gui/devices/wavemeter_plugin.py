import sys
import os
import InitializeCortex
from src.gui.assets.instrument_base import InstrumentBase, Parameter
from src.instruments.frontend.frontend_wavemeter import MqttWavemeter
from functools import partial
from PyQt6.QtCore import pyqtSlot
from src.gui.assets.csstyle import Style

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
        self.channel_sigmas = {} # Stores latest sigma for each channel

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
            get_cmd=partial(self.get_freq_wrapper, channel)
        ))

        # Setpoint Input
        self.add_parameter(Parameter(
            name=f"setpoint_ch{channel}",
            label=f"Ch {channel} Setpoint",
            param_type='float', # Generates a QLineEdit
            unit="THz",
            set_cmd=partial(self.set_setpoint_wrapper, channel),
            get_cmd=None
        ))

    def connect_instrument(self):
        for ch in range(1, 9):
            resource_id = f"{RESOURCE_BASE}{ch}"
            print(f"[{self.name}] Subscribing to {resource_id}...")
            try:
                driver = MqttWavemeter(resource_id)
                driver.open()
                self.drivers[ch] = driver

                # Connect Signals
                driver.frequency_updated.connect(partial(self.on_freq_update, channel=ch))
                driver.sigma_updated.connect(partial(self.on_sigma_update, channel=ch))

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

    @pyqtSlot(float)
    def on_freq_update(self, value, channel=None):
        param_name = f"frequency_ch{channel}"
        if param_name in self.parameters:
            param = self.parameters[param_name]
            if param.update_widget:
                text = f"{value:.6f}"
                param.update_widget(text)

    @pyqtSlot(float)
    def on_sigma_update(self, sigma, channel=None):
        self.channel_sigmas[channel] = sigma

        # Threshold: 10 MHz = 0.00001 THz
        STABILITY_THRESHOLD = 0.00001

        # 1. Check direct stability
        is_stable = sigma < STABILITY_THRESHOLD

        # 2. Check against Global Average of Stable Channels (as requested)
        stable_values = [s for s in self.channel_sigmas.values() if s < STABILITY_THRESHOLD]
        if stable_values:
            avg_stable_sigma = sum(stable_values) / len(stable_values)
            # Logic: "For every channel that is considered stable (or falls within this calculated Averaged Sigma range)"
            # Note: If sigma < AvgStable (< 10 MHz), it is necessarily stable (< 10 MHz).
            # So the condition effectively remains sigma < 10 MHz.
            # But we'll implement the check anyway if logic changes.
            if sigma < avg_stable_sigma:
                is_stable = True

        # Update Style
        param_name = f"frequency_ch{channel}"
        if param_name in self.parameters:
            param = self.parameters[param_name]
            if param.update_widget_style:
                if is_stable:
                    # Green text
                    param.update_widget_style("color: #4CAF50; font-weight: bold;")
                else:
                    # Default
                    param.update_widget_style(Style.Label.frequency_big)
