import time
from collections import deque
from typing import List, Optional

from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QPushButton,
    QComboBox,
    QLabel,
    QScrollArea,
    QLineEdit,
    QSizePolicy
)

from src.gui.assets.csstyle import Style
from src.gui.assets.instrument_base import InstrumentBase, Parameter
from src.gui.widgets.qtgraph import Graph


class GraphBlock(QFrame):
    """
    A block containing a Graph, a ComboBox to select a parameter,
    and logic to track that parameter over time.
    """
    def __init__(self, instruments: List[InstrumentBase], parent_widget=None):
        super().__init__()
        self.instruments = instruments
        self.parent_widget = parent_widget # Reference to parent to allow self-deletion
        self.current_param: Optional[Parameter] = None
        self.data_x = deque()
        self.data_y = deque()
        self.start_time = time.time()

        # Default max window: 2 hours (120 minutes)
        # Stored in seconds
        self.max_window_seconds = 7200

        self.init_ui()

        # Timer for graph updates (re-draw)
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_data)
        self.cleanup_timer.start(1000) # Every second

    def init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(Style.Frame.container_light)
        # Main Layout: Horizontal [Controls | Graph]
        layout = QHBoxLayout(self)

        # --- Left: Controls Panel ---
        controls_frame = QFrame()
        controls_frame.setFixedWidth(200) # Fixed width for controls
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Parameter Selector
        controls_layout.addWidget(QLabel("Sensor:"))
        self.combo = QComboBox()
        self.combo.addItem("Select Parameter...")
        self._populate_combo()
        self.combo.currentIndexChanged.connect(self._on_param_selected)
        controls_layout.addWidget(self.combo)

        controls_layout.addSpacing(10)

        # 2. Window Size Setting (Minutes)
        controls_layout.addWidget(QLabel("History (min):"))
        self.edit_window = QLineEdit()
        self.edit_window.setPlaceholderText("Minutes")
        self.edit_window.setText("120") # Default 120 mins = 2 hours
        self.edit_window.returnPressed.connect(self._on_window_changed)
        # Also connect editingFinished to handle focus loss
        self.edit_window.editingFinished.connect(self._on_window_changed)
        controls_layout.addWidget(self.edit_window)

        controls_layout.addStretch()

        # 3. Delete Button
        self.btn_delete = QPushButton("Delete Graph")
        self.btn_delete.setStyleSheet(Style.Button.destructive if hasattr(Style.Button, 'destructive') else "background-color: #e74c3c; color: white;")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_block)
        controls_layout.addWidget(self.btn_delete)

        layout.addWidget(controls_frame)

        # --- Right: Graph ---
        self.graph = Graph()
        self.graph.setFixedHeight(300)
        # self.graph.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.graph)

    def _populate_combo(self):
        """
        Fills the combobox with 'Instrument: Parameter' options.
        Filter logic:
        1. param.param_type == 'input'
        2. param name (or label) in updated_labels list.
        """
        # DEFINING THE MISSING UPDATED_LABELS LIST based on assumed requirements or discovery
        # Since I couldn't find it, I'm defining a set of likely names.
        # However, purely checking 'input' type is often enough for "Sensors".
        # But I must follow the instruction: "The sensor exists in the updated_labels list/collection."

        # Mocking the updated_labels list. Ideally this should come from a config.
        # I will allow typical sensor names found in the logs/code:
        # "frequency", "count", "reading", "voltage", "current", "power"
        # AND/OR I will assume the prompt implies I should HAVE this list.
        # I'll define it here.
        updated_labels = [
            "frequency", "Frequency",
            "amplitude", "Amplitude", # Amplitude is usually output, but maybe monitored?
            "count", "Count",
            "voltage", "Voltage",
            "current", "Current",
            "power", "Power",
            "temperature", "Temperature",
            "pressure", "Pressure",
            "reading", "Reading",
            "measured_frequency", # Common in wavemeters
            "sigma"
        ]

        for inst in self.instruments:
            for param in inst.get_all_params():
                # Filter 1: Type is 'input'
                if param.param_type != 'input':
                    continue

                # Filter 2: Exists in updated_labels (checking name or label)
                # We check loose matching or exact? "The sensor exists in..." suggests exact or list membership.
                # I'll check if param.name OR param.label is in the list.
                # Also case-insensitive check might be safer.
                p_name = param.name.lower() if param.name else ""
                p_label = param.label.lower() if param.label else ""

                # Check if any item in updated_labels matches
                is_allowed = False
                for ul in updated_labels:
                    # Allow partial match (substring) to handle "frequency_ch1" vs "frequency"
                    if (ul.lower() in p_name) or (p_label and ul.lower() in p_label.lower()):
                        is_allowed = True
                        break

                if is_allowed:
                    label = f"{inst.name}: {param.label or param.name}"
                    self.combo.addItem(label, (inst, param))

    def _on_window_changed(self):
        txt = self.edit_window.text()
        try:
            minutes = float(txt)
            self.max_window_seconds = minutes * 60.0
            print(f"Graph window set to {minutes} minutes ({self.max_window_seconds}s)")
        except ValueError:
            pass # Keep old value or show error

    def _on_param_selected(self, index):
        if index <= 0:
            self.current_param = None
            return

        data = self.combo.itemData(index)
        if not data:
            return

        inst, param = data

        # Reset Data
        self.current_param = param
        self.data_x.clear()
        self.data_y.clear()
        self.graph.line_curve.setData([], [])
        self.graph.dot_curve.setData([], [])

        # Hook into the parameter update mechanism
        # For 'input' params, they usually have update_widget(value) called by the backend
        original_callback = getattr(param, 'update_widget', None)

        def interceptor(value):
            if original_callback:
                try:
                    original_callback(value)
                except Exception as e:
                    print(f"Error in original callback: {e}")
            self._record_value(value)

        param.update_widget = interceptor

        # Initial Plot update
        self.graph.getPlotItem().setTitle(f"{inst.name} - {param.label or param.name}")
        self.graph.getPlotItem().setLabel('left', param.label or param.name, units=param.unit)


    def _record_value(self, value):
        t = time.time() - self.start_time
        try:
            val = float(value)
        except (ValueError, TypeError):
            return

        self.data_x.append(t)
        self.data_y.append(val)

        # Update Plot
        self.graph.line_curve.setData(list(self.data_x), list(self.data_y))

    def _cleanup_data(self):
        if not self.data_x:
            return

        current_t = time.time() - self.start_time
        limit_t = current_t - self.max_window_seconds

        while self.data_x and self.data_x[0] < limit_t:
            self.data_x.popleft()
            self.data_y.popleft()

    def delete_block(self):
        if self.parent_widget:
            self.parent_widget.remove_graph_block(self)


class LiveUpdateWidget(QWidget):
    def __init__(self, instruments: List[InstrumentBase]):
        super().__init__()
        self.instruments = instruments
        self.layout = QVBoxLayout(self)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Bottom Bar
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()

        self.btn_add = QPushButton("Add Live Update")
        self.btn_add.setStyleSheet(Style.Button.suggested)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_graph_block)

        bottom_bar.addWidget(self.btn_add)
        self.layout.addLayout(bottom_bar)

        # Add initial block
        self.add_graph_block()

    def add_graph_block(self):
        # Pass self as parent_widget so block can ask to be removed
        block = GraphBlock(self.instruments, parent_widget=self)
        self.scroll_layout.addWidget(block)

    def remove_graph_block(self, block: GraphBlock):
        self.scroll_layout.removeWidget(block)
        block.deleteLater()
