from dataclasses import dataclass
from typing import Callable, Any, Optional

@dataclass
class Parameter:
    name: str
    label: str
    param_type: str  # 'bool', 'float', 'int', 'str'
    set_cmd: Optional[Callable[[Any], None]] = None # Function to set value
    get_cmd: Optional[Callable[[], Any]] = None     # Function to read value
    unit: str = ""
    scannable: bool = False
    
class InstrumentBase:
    def __init__(self, name):
        self.name = name
        self.parameters = {} # Dictionary to store params

    def add_parameter(self, param: Parameter):
        self.parameters[param.name] = param

    def connect_instrument(self):
        """Override this to connect to physical hardware"""
        pass

    def get_all_params(self):
        return self.parameters.values()
