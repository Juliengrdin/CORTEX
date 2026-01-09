import os
import sys
import importlib.util
from collections import defaultdict
from typing import List, Optional
from PyQt6.QtCore import Qt, QSize
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
    QListWidget,
    QStackedWidget,
    QListWidgetItem,
    QSizePolicy
)

# --- Local Imports ---
# Assuming this file is now in src/gui/tabs/
# and imports should be adjusted relative to the root if PYTHONPATH is set correctly,
# or relative to this file.
# The original builder.py used absolute imports starting with 'src.'.
# We should keep using absolute imports if possible.

from src.gui.assets.csstyle import Style
from src.gui.assets.instrument_base import InstrumentBase, Parameter
from src.gui.widgets.smaller_toggle import AnimatedToggle
from src.gui.widgets.flow_layout import FlowLayout


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
        
        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet(Style.Default.light)
        # Limit width for responsive grid
        self.setFixedWidth(280)

        # 1. Header (Title + Divider)
        self._init_header()

        # 2. Parameter Controls
        for param in self.instrument.get_all_params():
            self._add_parameter_row(param)

    @property
    def scannable(self):
        # Scan through all parameters to see if any are scannable
        return any(p.scannable for p in self.instrument.get_all_params())

    def _init_header(self):
        """Creates the bold title and horizontal divider line."""
        title = QLabel(self.instrument.name)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
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
            btn.setStyleSheet(Style.Button.suggested)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda: self.send_command(param, input_widget.text()))
            row_layout.addWidget(btn)
            

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
                 param.update_widget_rich = widget.setText
            if hasattr(param, 'update_widget_style'):
                 param.update_widget_style = widget.setStyleSheet
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


class InstrumentPanel(QWidget):
    """
    The Main Dashboard Panel.
    Loads plugins and arranges them in a Discord-style layout:
    - Left Sidebar (Tabs/Categories)
    - Right Content Area (Responsive Grid/Flow)
    """
    def __init__(self, devices_path: Optional[str] = None):
        super().__init__()
        
        # Main Layout (Splitter-like)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Sidebar (Category List)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150)
        self.sidebar.setStyleSheet(Style.List.light)
        self.sidebar.currentItemChanged.connect(self._on_category_changed)
        self.main_layout.addWidget(self.sidebar)
        
        # 2. Content Area (Stacked Widget)
        self.content_stack = QStackedWidget()
        self.content_stack.setContentsMargins(10, 10, 10, 10)
        self.content_stack.setStyleSheet(Style.Frame.container_light)
        self.main_layout.addWidget(self.content_stack)
        
        # Store category widgets to manage indices
        self.category_pages = {}

        # Store loaded instruments for external access
        self.loaded_instruments = []

        # 3. Load & Organize Instruments
        if not devices_path:
            # We need to find the devices directory relative to THIS file or absolute.
            # Original code: devices_path = os.path.join(os.path.dirname(__file__), "devices")
            # If this file is in src/gui/tabs/devices_tab.py, then devices is in ../devices
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            devices_path = os.path.join(base_dir, "devices")

        self._load_and_display_plugins(devices_path)

        # Select first item by default
        if self.sidebar.count() > 0:
            self.sidebar.setCurrentRow(0)

    def _load_and_display_plugins(self, plugin_dir: str):
        """Loads python files and creates pages for each category."""
        self.loaded_instruments = self._load_plugins_from_disk(plugin_dir)
        
        # Group by Category
        grouped = defaultdict(list)
        for inst in self.loaded_instruments:
            cat = getattr(inst, 'category', 'Uncategorized')
            grouped[cat].append(inst)
            
        # Sort Categories
        def category_sort_key(name):
            special_categories = ["Miscellaneous", "Divers", "Other", "Uncategorized"]
            priority = 1 if name in special_categories else 0
            return (priority, name)

        sorted_categories = sorted(grouped.keys(), key=category_sort_key)

        for category_name in sorted_categories:
            instruments = grouped[category_name]
            instruments.sort(key=lambda inst: inst.name)
            
            # Create Page for Category
            page_widget = QWidget()
            # Use FlowLayout for responsive grid
            flow_layout = FlowLayout(page_widget, margin=10, spacing=10)

            for inst in instruments:
                frame = InstrumentFrame(inst)
                flow_layout.addWidget(frame)

            # Wrap in Scroll Area
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(page_widget)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setStyleSheet(Style.Scroll.transparent)

            # Add to Stack
            self.content_stack.addWidget(scroll)
            self.category_pages[category_name] = scroll

            # Add to Sidebar
            item = QListWidgetItem(category_name)
            self.sidebar.addItem(item)

    def _on_category_changed(self, current_item, previous_item):
        if not current_item:
            return
        category_name = current_item.text()
        if category_name in self.category_pages:
            widget = self.category_pages[category_name]
            self.content_stack.setCurrentWidget(widget)

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
                                # Instantiate and add
                                loaded_instruments.append(attr())
                except Exception as e:
                    print(f">> [Loader] Failed to load {filename}: {e}")
                    
        return loaded_instruments
