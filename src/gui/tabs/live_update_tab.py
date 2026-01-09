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
        
        self.active_hook_param = None      # To track which param we modified
        self.active_original_callback = None #

        # Default max window: 2 hours (120 minutes)
        # Stored in seconds
        self.max_window_seconds = 60 #avoid high memory usage

        # State control
        self.paused = False

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

        # --- Left Column: Controls Panel ---
        controls_frame = QFrame()
        controls_frame.setFixedWidth(150) # Fixed width for controls
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Parameter Selector
        controls_layout.addWidget(QLabel("Sensor Parameter:"))
        self.combo = QComboBox()
        #self.combo.setStyleSheet(Style.Input.combobox_light)
        self.combo.addItem("Select Parameter...")
        self._populate_combo()
        self.combo.currentIndexChanged.connect(self._on_param_selected)
        controls_layout.addWidget(self.combo)

        # 1b. Current Value Display
        self.lbl_current_value = QLabel("Value: ---")
        self.lbl_current_value.setStyleSheet("font-weight: bold; font-size: 14px;")
        controls_layout.addWidget(self.lbl_current_value)

        controls_layout.addSpacing(10)

        # 2. Window Size Setting (Minutes)
        controls_layout.addWidget(QLabel("History (min):"))
        self.edit_window = QLineEdit()
        self.edit_window.setStyleSheet(Style.Input.line_edit_light)
        self.edit_window.setPlaceholderText("Minutes")
        self.edit_window.setText("1") # Default 1 mins
        self.edit_window.returnPressed.connect(self._on_window_changed)
        self.edit_window.editingFinished.connect(self._on_window_changed)
        controls_layout.addWidget(self.edit_window)

        controls_layout.addSpacing(10)

        # 3. Control Buttons (Start, Stop, Reset)

        # Start
        self.btn_start = QPushButton("Start")
        self.btn_start.setStyleSheet(Style.Button.start)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.clicked.connect(self.start_graph)
        controls_layout.addWidget(self.btn_start)

        # Stop
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setStyleSheet(Style.Button.stop)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self.stop_graph)
        controls_layout.addWidget(self.btn_stop)

        # Reset
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setStyleSheet(Style.Button.reset)
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_graph)
        controls_layout.addWidget(self.btn_reset)

        controls_layout.addStretch()

        # 4. Delete Button
        self.btn_delete = QPushButton("Delete Graph")
        self.btn_delete.setStyleSheet(Style.Button.simple_dark)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_block)
        controls_layout.addWidget(self.btn_delete)

        layout.addWidget(controls_frame)

        # --- Right Column: Graph ---
        self.graph = Graph()
        #self.graph.setFixedHeight(300)
        # self.graph.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.graph)

    def _populate_combo(self):
        """
        Fills the combobox with 'Instrument: Parameter' options.
        Filter logic:
        1. param.param_type == 'input'
        2. param name (or label) in updated_labels list.
        """
        updated_labels = [
            "frequency", "Frequency",
            "amplitude", "Amplitude",
            "count", "Count",
            "voltage", "Voltage",
            "current", "Current",
            "power", "Power",
            "temperature", "Temperature",
            "pressure", "Pressure",
            "reading", "Reading",
            "measured_frequency",
            "sigma"
        ]

        for inst in self.instruments:
            for param in inst.get_all_params():
                # Filter 1: Type is 'input'
                if param.param_type != 'input':
                    continue

                # Filter 2: Exists in updated_labels (checking name or label)
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
            pass

    def _on_param_selected(self, index):
        # 1. DISCONNECT THE OLD PARAMETER FIRST
        self._unhook_current_param()

        if index <= 0:
            self.current_param = None
            self.reset_graph()
            return

        data = self.combo.itemData(index)
        if not data:
            return

        inst, param = data

        # Reset Graph Data
        self.current_param = param
        self.reset_graph()

        # 2. SAVE THE ORIGINAL CALLBACK
        original_callback = getattr(param, 'update_widget', None)
        
        # 3. DEFINE THE NEW INTERCEPTOR
        def interceptor(value):
            # Pass data to the original GUI widget (if any)
            if original_callback:
                try:
                    original_callback(value)
                except Exception as e:
                    print(f"Error in original callback: {e}")
            # Pass data to our graph
            self._record_value(value)

        # 4. OVERWRITE THE CALLBACK (HOOK)
        param.update_widget = interceptor

        # 5. STORE STATE SO WE CAN UNDO THIS LATER
        self.active_hook_param = param
        self.active_original_callback = original_callback

        # Update Plot Labels
        self.graph.getPlotItem().setTitle(f"{inst.name} - {param.label or param.name}")
        self.graph.getPlotItem().setLabel('left', param.label or param.name, units=param.unit)


    def _record_value(self, value):
        # Always update current value label if possible, even if paused?
        # Usually "Stop" means stop plotting, but maybe still show value?
        # Prompt says "Pauses data plotting". I will allow value update in label but not plot.
        # But for consistency, let's keep it simple: Stop means stop everything for this graph block.
        # Or maybe update label but not graph.
        # I'll update label always if I can parse it, or display string.

        display_str = str(value)
        # Strip HTML if present for the label (rudimentary)
        import re
        clean_str = re.sub('<[^<]+?>', '', display_str)
        self.lbl_current_value.setText(f"Value: {clean_str}")

        if self.paused:
            return

        t = time.time() - self.start_time
        try:
            val = float(value)
        except (ValueError, TypeError):
            # Attempt to handle html string if necessary, but backend should send float mostlly TODO
            try:
                # Basic cleanup for common cases (e.g. "123.456 V")
                import re
                # extract first number
                match = re.search(r"[-+]?\d*\.\d+|\d+", str(value))
                if match:
                    val = float(match.group())
                else:
                    return
            except Exception:
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

    def start_graph(self):
        self.paused = False
        print("Graph Resumed")

    def stop_graph(self):
        self.paused = True
        print("Graph Paused")

    def reset_graph(self):
        self.data_x.clear()
        self.data_y.clear()
        self.graph.line_curve.setData([], [])
        self.graph.dot_curve.setData([], [])
        print("Graph Reset")

    def delete_block(self):
        # Clean up the hook on the instrument before dying
        self._unhook_current_param()
        
        if self.parent_widget:
            self.parent_widget.remove_graph_block(self)
            
    def _unhook_current_param(self):
        """Restores the original update_widget function for the previous parameter."""
        if self.active_hook_param is not None:
            # Restore the original function we saved earlier
            if self.active_original_callback:
                self.active_hook_param.update_widget = self.active_original_callback
            else:
                # If there was no callback originally, just remove ours (set to None or dummy)
                # Usually keeping it as is or None is safe if it was None.
                # Ideally, if it was None, we leave it, but we can't easily 'delete' the assignment
                # unless we assigned a dummy. 
                # Better approach: Just restore whatever self.active_original_callback was.
                self.active_hook_param.update_widget = self.active_original_callback
            
            # Clear our tracking variables
            self.active_hook_param = None
            self.active_original_callback = None


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
