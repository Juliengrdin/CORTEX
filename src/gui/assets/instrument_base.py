from dataclasses import dataclass
from typing import Callable, Any, Optional
from PyQt6.QtCore import QObject

@dataclass
class Parameter:
    name: str
    label: str
    param_type: str  # 'bool', 'float', 'int', 'str', 'input'
    set_cmd: Optional[Callable[[Any], None]] = None # Function to set value
    get_cmd: Optional[Callable[[], Any]] = None     # Function to read value
    unit: str = ""
    
    # New field to allow the plugin to update the UI
    update_widget: Optional[Callable[[Any], None]] = None
    # New field to allow the plugin to update the UI style
    update_widget_style: Optional[Callable[[str], None]] = None

    @property
    def scannable(self) -> bool:
        return self.param_type == 'float'

class InstrumentBase(QObject):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.parameters = {} # Dictionary to store params

    def add_parameter(self, param: Parameter):
        self.parameters[param.name] = param

    def connect_instrument(self):
        """Override this to connect to physical hardware"""
        pass

    def get_all_params(self):
        return self.parameters.values()
