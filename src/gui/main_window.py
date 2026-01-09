import sys
import time
from collections import deque
from typing import List, Optional

from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QStackedWidget,
    QListWidgetItem,
    QFrame,
    QPushButton,
    QComboBox,
    QLabel,
    QScrollArea,
    QDoubleSpinBox
)

from src.gui.builder import InstrumentPanel
from src.gui.assets.csstyle import Style
from src.gui.assets.instrument_base import InstrumentBase, Parameter
from src.gui.widgets.qtgraph import Graph

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CORTEX Laboratory Dashboard")
        self.resize(1200, 800)

        # Main Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Navigation
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet(Style.List.light)
        self.sidebar.addItem("Devices")
        self.sidebar.addItem("Live Update")
        self.sidebar.addItem("Scan")
        self.sidebar.setCurrentRow(0)
        self.sidebar.currentRowChanged.connect(self.display_page)
        main_layout.addWidget(self.sidebar)

        # 2. Content Stack
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0) # Let pages handle margins
        main_layout.addWidget(self.stack)

        # --- Page 1: Devices (Principal) ---
        self.devices_panel = InstrumentPanel()
        self.stack.addWidget(self.devices_panel)

        # --- Page 2: Live Update ---
        # We pass the loaded instruments to the LiveUpdateWidget
        self.live_update_page = LiveUpdateWidget(self.devices_panel.loaded_instruments)
        self.stack.addWidget(self.live_update_page)

        # --- Page 3: Scan ---
        self.scan_page = QWidget()
        scan_layout = QVBoxLayout(self.scan_page)
        scan_layout.addWidget(QLabel("Scan Page (Placeholder)"))
        self.stack.addWidget(self.scan_page)

    def display_page(self, index):
        self.stack.setCurrentIndex(index)


class GraphBlock(QFrame):
    """
    A block containing a Graph, a ComboBox to select a parameter,
    and logic to track that parameter over time.
    """
    def __init__(self, instruments: List[InstrumentBase]):
        super().__init__()
        self.instruments = instruments
        self.current_param: Optional[Parameter] = None
        self.data_x = deque()
        self.data_y = deque()
        self.start_time = time.time()

        # Default max window: 2 hours (7200 seconds)
        self.max_window_seconds = 7200

        self.init_ui()

        # Timer for graph updates (re-draw)
        # We don't necessarily poll data here, but we refresh the plot
        # However, if we rely on callbacks, we just append data there.
        # But we need to prune old data.
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_data)
        self.cleanup_timer.start(1000) # Every second

    def init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(Style.Frame.container_light)
        layout = QVBoxLayout(self)

        # Controls Row
        controls_layout = QHBoxLayout()

        # Parameter Selector
        self.combo = QComboBox()
        self.combo.addItem("Select Parameter...")
        self._populate_combo()
        self.combo.currentIndexChanged.connect(self._on_param_selected)
        controls_layout.addWidget(self.combo)

        # Window Size Setting
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("History (hrs):"))
        self.spin_window = QDoubleSpinBox()
        self.spin_window.setRange(0.1, 24.0)
        self.spin_window.setValue(2.0)
        self.spin_window.setSuffix(" h")
        self.spin_window.valueChanged.connect(self._on_window_changed)
        controls_layout.addWidget(self.spin_window)

        layout.addLayout(controls_layout)

        # Graph
        self.graph = Graph()
        self.graph.setFixedHeight(300) # Reasonable height
        layout.addWidget(self.graph)

    def _populate_combo(self):
        """Fills the combobox with 'Instrument: Parameter' options."""
        # Use user role to store the actual (inst, param) tuple
        for inst in self.instruments:
            for param in inst.get_all_params():
                # Only track numbers (float/int) usually, but maybe bools too?
                # The prompt says "track its evolution". Graph usually implies numbers.
                if param.param_type in ["float", "int", "bool"]:
                    label = f"{inst.name}: {param.name}"
                    self.combo.addItem(label, (inst, param))

    def _on_window_changed(self, val):
        self.max_window_seconds = val * 3600

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
        # 1. Existing callback?
        original_callback = getattr(param, 'update_widget', None)

        # 2. Define our interceptor
        def interceptor(value):
            # Call original if exists
            if original_callback:
                try:
                    original_callback(value)
                except Exception as e:
                    print(f"Error in original callback: {e}")

            # Record data
            self._record_value(value)

        # 3. Apply interceptor
        # Note: This is invasive. If multiple GraphBlocks select the same param,
        # they might chain indefinitely or overwrite.
        # For this task, we assume single listener or just overwrite.
        # But chaining is safer.
        param.update_widget = interceptor

        # Initial Plot update
        self.graph.getPlotItem().setTitle(f"{inst.name} - {param.label or param.name}")
        self.graph.getPlotItem().setLabel('left', param.label or param.name, units=param.unit)


    def _record_value(self, value):
        t = time.time() - self.start_time
        try:
            val = float(value)
        except (ValueError, TypeError):
            return # Ignore non-numeric

        self.data_x.append(t)
        self.data_y.append(val)

        # Update Plot
        self.graph.line_curve.setData(list(self.data_x), list(self.data_y))
        # self.graph.dot_curve.setData(list(self.data_x), list(self.data_y))

    def _cleanup_data(self):
        if not self.data_x:
            return

        current_t = time.time() - self.start_time
        limit_t = current_t - self.max_window_seconds

        while self.data_x and self.data_x[0] < limit_t:
            self.data_x.popleft()
            self.data_y.popleft()

        # Refresh plot if data changed
        # (Optional optimization: only setData if popped)
        # self.graph.line_curve.setData(list(self.data_x), list(self.data_y))


class LiveUpdateWidget(QWidget):
    def __init__(self, instruments: List[InstrumentBase]):
        super().__init__()
        self.instruments = instruments
        self.layout = QVBoxLayout(self)

        # Scroll Area for Graphs
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # "Add Live Update" Button
        self.btn_add = QPushButton("Add Live Update")
        self.btn_add.setStyleSheet(Style.Button.suggested)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_graph_block)

        # Bottom Bar
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.btn_add)
        self.layout.addLayout(bottom_bar)

        # Add initial block
        self.add_graph_block()

    def add_graph_block(self):
        block = GraphBlock(self.instruments)
        self.scroll_layout.addWidget(block)
