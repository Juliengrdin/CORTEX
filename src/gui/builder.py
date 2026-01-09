import os
import sys
import importlib.util
from collections import defaultdict
from typing import List, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

# --- Local Imports ---
import InitializeCortex
from src.gui.assets.csstyle import Style
from src.gui.assets.instrument_base import InstrumentBase, Parameter
from src.gui.widgets.smaller_toggle import AnimatedToggle


# ==============================================================================
#   ENVIRONMENT SETUP
# ==============================================================================

def configure_mqtt_environment():
    """
    Detects if the environment requires a Mock MQTT client.
    Patches sys.modules to substitute paho.mqtt with the mock if needed.
    """
    mock_mqtt = None
    
    # 1. Try importing the mock from known locations
    try:
        import tests.mock_paho_mqtt_plugin as mock_mqtt
    except ImportError:
        try:
            import mock_paho_mqtt_plugin as mock_mqtt
        except ImportError:
            pass

    # 2. Apply patch if mock is found
    if mock_mqtt:
        sys.modules["paho"] = mock_mqtt
        sys.modules["paho.mqtt"] = mock_mqtt
        sys.modules["paho.mqtt.client"] = mock_mqtt
        mock_mqtt.client = mock_mqtt
        print(">> [System] WARNING: Running with MOCK MQTT Environment")

# Run setup immediately
configure_mqtt_environment()


# ==============================================================================
#   UI COMPONENTS
# ==============================================================================

class InstrumentFrame(QFrame):
    """
    A widget representing the controls for a single Instrument.
    Generates UI elements dynamically based on the instrument's parameters.
    """
    def __init__(self, instrument: InstrumentBase):
        super().__init__()
        self.instrument = instrument
        self.scannable = False
        
        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet(Style.Default.light)

        # 1. Header (Title + Divider)
        self._init_header()

        # 2. Parameter Controls
        for param in self.instrument.get_all_params():
            self._add_parameter_row(param)

    def _init_header(self):
        """Creates the bold title and horizontal divider line."""
        title = QLabel(self.instrument.name)
        title.setStyleSheet("font-weight: bold; margin-bottom: 4px; color: #333333;")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #DDDDDD;")
        self.layout.addWidget(line)

    def _add_parameter_row(self, param: Parameter):
        """Creates a labeled row with an input widget (Toggle or LineEdit)."""
        row_layout = QHBoxLayout()
        
        # Label
        if param.label is not None:
            label = QLabel(f"{param.label}:")
            row_layout.addWidget(label)
        
        # Input Widget
        input_widget = self._create_input_widget(param, row_layout)
        
        # 'Send' Button (Only for non-boolean params)
        if param.param_type != "bool" and param.param_type != 'input':
            btn = QPushButton("Send")
            btn.setStyleSheet(Style.Button.suggested) # Fixed reference
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Connect: Get text from input_widget when clicked
            btn.clicked.connect(lambda: self.send_command(param, input_widget.text()))
            row_layout.addWidget(btn)
            
        # Track scannability for higher-level logic (if needed)
        if param.scannable:
            self.scannable = True

        self.layout.addLayout(row_layout)

    def _create_input_widget(self, param: Parameter, parent_layout: QHBoxLayout):
        """Helper to create the correct widget type."""
        if param.param_type == "bool":
            widget = AnimatedToggle()
            # Connect direct toggle action
            widget.toggled.connect(lambda state: self.send_command(param, state))
            parent_layout.addWidget(widget)
            # Register the widget if the parameter needs it
            if hasattr(param, 'update_widget'):
                 param.update_widget = widget.setChecked
            return widget
        
        elif param.param_type in ["float", "int", "str"]:
            widget = QLineEdit()
            widget.setPlaceholderText(str(param.unit))
            parent_layout.addWidget(widget)
            if hasattr(param, 'update_widget'):
                 param.update_widget = widget.setText
            return widget
            
        elif param.param_type == 'input':
            widget = QLabel("_")
            widget.setStyleSheet(Style.Label.frequency_big)
            parent_layout.addWidget(widget)
            if hasattr(param, 'update_widget'):
                 param.update_widget = widget.setText
            return widget
            
        return QWidget() # Fallback empty widget

    def send_command(self, param: Parameter, value):
        """Handles type conversion and execution of the instrument command."""
        try:
            # 1. Convert Type
            if param.param_type == "float":
                value = float(value)
            elif param.param_type == "int":
                value = int(value)
            
            # 2. Execute
            if param.set_cmd:
                param.set_cmd(value)
                print(f"[{self.instrument.name}] Set {param.name} = {value}")
                
        except ValueError:
            print(f"[{self.instrument.name}] Error: Invalid input for {param.name}")


class CategoryColumn(QFrame):
    """
    A vertical column representing one category of instruments (e.g., 'Lasers').
    Contains a Title and a ScrollArea for the instruments.
    """
    def __init__(self, category_name: str, instruments: List[InstrumentBase]):
        super().__init__()
        self.setObjectName("CategoryFrame")
        self.setStyleSheet(Style.Frame.container_light)
        self.setFixedWidth(300) # Slightly wider for better breathing room

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # 1. Title
        title = QLabel(category_name)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(Style.Label.title_light)
        layout.addWidget(title)
        
        # 2. Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(Style.Scroll.transparent)
        
        # 3. Container for Instruments
        container = QWidget()
        v_layout = QVBoxLayout(container)
        v_layout.setSpacing(10)
        v_layout.setContentsMargins(5, 5, 5, 5)
        
        for inst in instruments:
            frame = InstrumentFrame(inst)
            v_layout.addWidget(frame)
            
        v_layout.addStretch() # Push items to top
        
        self.scroll.setWidget(container)
        layout.addWidget(self.scroll)


class InstrumentPanel(QWidget):
    """
    The Main Dashboard Panel.
    Loads plugins dynamically and arranges them into horizontal category columns.
    """
    def __init__(self, devices_path: Optional[str] = None):
        super().__init__()
        
        # Main Layout (Fill the window)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Horizontal Scroll Area (Holds the columns)
        self.h_scroll = QScrollArea()
        self.h_scroll.setWidgetResizable(True)
        self.h_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.h_scroll.setStyleSheet(Style.Scroll.Htransparent)
        
        # 2. Container for Columns
        self.columns_container = QWidget()
        self.columns_layout = QHBoxLayout(self.columns_container)
        self.columns_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.columns_layout.setSpacing(15)
        self.columns_layout.setContentsMargins(15, 15, 15, 15)
        
        self.h_scroll.setWidget(self.columns_container)
        main_layout.addWidget(self.h_scroll)

        # 3. Load & Organize Instruments
        if not devices_path:
            # Default to 'devices' folder in current directory
            devices_path = os.path.join(os.path.dirname(__file__), "devices")

        self._load_and_display_plugins(devices_path)

    def _load_and_display_plugins(self, plugin_dir: str):
        """Loads python files from directory and creates UI columns."""
        all_instruments = self._load_plugins_from_disk(plugin_dir)
        
        # Group by Category
        grouped = defaultdict(list)
        for inst in all_instruments:
            cat = getattr(inst, 'category', 'Uncategorized')
            grouped[cat].append(inst)
            
        # --- FIX: Custom Sort Order ---
        def category_sort_key(name):
            # If name is in this list, return 1 (pushes to end). Else 0 (stays at top).
            special_categories = ["Miscellaneous", "Divers", "Other", "Uncategorized"]
            priority = 1 if name in special_categories else 0
            return (priority, name)

        # Apply the custom sort key
        sorted_categories = sorted(grouped.keys(), key=category_sort_key)

        for category_name in sorted_categories:
            instruments = grouped[category_name]
            
            # Sort Instruments within the Category Alphabetically
            instruments.sort(key=lambda inst: inst.name)
            
            column = CategoryColumn(category_name, instruments)
            self.columns_layout.addWidget(column)

    def _load_plugins_from_disk(self, plugin_dir: str) -> List[InstrumentBase]:
        """Scans folder for .py files and instantiates InstrumentBase subclasses."""
        loaded_instruments = []
        
        if not os.path.exists(plugin_dir):
            print(f">> [Loader] Directory not found: {plugin_dir}")
            return []

        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py"):
                path = os.path.join(plugin_dir, filename)
                try:
                    # Dynamic Import
                    spec = importlib.util.spec_from_file_location("module.name", path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Inspect module for InstrumentBase subclasses
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                issubclass(attr, InstrumentBase) and 
                                attr is not InstrumentBase):
                                print(f"DEBUG: Loading '{attr().name}' from file: {filename} (Class: {attr_name})")
                                # Instantiate and add
                                loaded_instruments.append(attr())
                except Exception as e:
                    print(f">> [Loader] Failed to load {filename}: {e}")
                    
        return loaded_instruments


# ==============================================================================
#   MAIN ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Optional: Apply Global Theme
    # app.setStyleSheet(Style.Default.light) 
    
    win = QMainWindow()
    win.setWindowTitle("CORTEX Laboratory Dashboard")
    win.resize(960, 500)
    
    panel = InstrumentPanel()
    win.setCentralWidget(panel)
    
    win.show()
    sys.exit(app.exec())
