import sys
import os
import InitializeCortex
from src.gui.assets.instrument_base import InstrumentBase, Parameter
from src.instruments.frontend.frontend_camera import MqttCamera
from PyQt6.QtCore import pyqtSlot

# ==============================================================================
#   SECTION 1: USER CONFIGURATION
# ==============================================================================
DISPLAY_NAME = "Hamamatsu Camera"
CATEGORY = 'Sensor'
RESOURCE_ID  = "HAMAMATSU/0000"

# ==============================================================================
#   SECTION 2: INSTRUMENT LOGIC
# ==============================================================================
class CameraPlugin(InstrumentBase):
    def __init__(self):
        super().__init__(DISPLAY_NAME)
        self.driver = None
        self.category = CATEGORY

        self.add_parameter(Parameter(
            name="total_count",
            label="Total Count",
            param_type='input',
            unit="",
            set_cmd=None,
            get_cmd=None,
            scannable=False
        ))

        self.connect_instrument()

    def connect_instrument(self):
        print(f"[{self.name}] Subscribing to {RESOURCE_ID}...")
        try:
            self.driver = MqttCamera(RESOURCE_ID)
            self.driver.open()
            self.driver.count_updated.connect(self.on_count_update)
        except Exception as e:
            print(f"[{self.name}] Connection failed: {e}")

    @pyqtSlot(int)
    def on_count_update(self, value):
        param = self.parameters.get("total_count")
        if param and param.update_widget:
            param.update_widget(str(value))
