import sys
import yaml
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGroupBox, QLabel, QLineEdit, 
                             QCheckBox, QPushButton, QComboBox, QScrollArea, QFrame)
from PyQt6.QtCore import Qt

CONFIG_FILE = "config/logging.yaml"

class ExperimentGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modular Experiment Control")
        self.resize(1200, 800) # Made wider for columns

        # 1. Main Container (The Horizontal Scroll Area)
        self.main_scroll = QScrollArea()
        self.main_scroll.setWidgetResizable(True)
        self.setCentralWidget(self.main_scroll)

        # The widget inside the scroll area that holds the columns
        self.columns_container = QWidget()
        self.columns_layout = QHBoxLayout(self.columns_container)
        self.columns_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.main_scroll.setWidget(self.columns_container)

  

        # 3. Build UI
        self.load_config_and_build()

    def load_config_and_build(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading YAML: {e}")
            return

        # 4. Sort Devices by Category
        categories = {} # Dict: {'sensor': [dev1, dev2], 'actuator': [dev3]}
        
        for device in config.get("devices", []):
            cat = device.get("category", "Uncategorized")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(device)

        # 5. Create a Column for each Category
        for cat_name, devices in categories.items():
            self.create_category_column(cat_name, devices)

    def create_category_column(self, category_name, devices):
        # A. Vertical Scroll Area for this category
        cat_scroll = QScrollArea()
        cat_scroll.setWidgetResizable(True)
        cat_scroll.setFixedWidth(350) # Fixed width for columns
        
        # B. Container widget inside the scroll area
        cat_widget = QWidget()
        cat_layout = QVBoxLayout(cat_widget)
        cat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # C. Category Title (Optional Header)
        title = QLabel(f"--- {category_name.upper()} ---")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 10px;")
        cat_layout.addWidget(title)

        # D. Add Devices to this column
        for device_data in devices:
            if "gui" in device_data:
                group_box = self.create_device_panel(device_data)
                cat_layout.addWidget(group_box)

        # Finish Column Setup
        cat_scroll.setWidget(cat_widget)
        self.columns_layout.addWidget(cat_scroll)

    def create_device_panel(self, device_data):
        group = QGroupBox(device_data["name"])
        main_layout = QVBoxLayout()
        
        for control in device_data["gui"]:
            
            # --- CASE A: Explicit Horizontal Row (The new feature) ---
            if control.get("layout") == "row":
                row_layout = QHBoxLayout()
                # Loop through the items inside this row
                for item in control.get("items", []):
                    # 1. Add Label (if exists)
                    if "label" in item:
                        row_layout.addWidget(QLabel(item["label"]))
                    
                    # 2. Add Widget
                    widget = self.build_single_widget(item)
                    if widget:
                        row_layout.addWidget(widget)
                
                main_layout.addLayout(row_layout)

            # --- CASE B: Standard Single Line (Label + Widget) ---
            else:
                row_layout = QHBoxLayout()
                
                # 1. Add Label (if exists)
                if "label" in control:
                    row_layout.addWidget(QLabel(control["label"]))
                
                # 2. Add Widget
                widget = self.build_single_widget(control)
                if widget:
                    row_layout.addWidget(widget)
                    
                main_layout.addLayout(row_layout)

        group.setLayout(main_layout)
        return group

    # --- HELPER FUNCTION: Creates the actual widget object ---
    def build_single_widget(self, config):
        w_type = config.get("widget")
        widget = None
        
        # 1. Line Edit
        if w_type == "lineedit":
            widget = QLineEdit()
            widget.setText(str(config.get("default", "")))
            
        # 2. Checkbox
        elif w_type == "checkbox":
            widget = QCheckBox()
            widget.setChecked(config.get("default", False))

        # 3. Button
        elif w_type == "button":
            # Use 'label_btn' for the text inside the button
            btn_txt = config.get("label_btn", config.get("label", "Button"))
            widget = QPushButton(btn_txt)

        # 4. Combobox
        elif w_type == "combobox":
            widget = QComboBox()
            options = config.get("options", [])
            widget.addItems([str(opt) for opt in options])
            default_val = str(config.get("default"))
            index = widget.findText(default_val)
            if index >= 0:
                widget.setCurrentIndex(index)

        # 5. Display Label (The big blue one)
        elif w_type == "label":
            widget = QLabel(str(config.get("default", "")))
            widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        # --- Common Properties ---
        if widget:
            # Apply Width if specified
            if "width" in config:
                widget.setFixedWidth(config["width"])

            # Apply CSS Class
            if "css_class" in config:
                widget.setProperty("cssClass", config["css_class"])
            
            # Set ID for MQTT
            widget.setProperty("mqtt_id", config.get("id"))

        return widget
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # LOAD STYLESHEET


    window = ExperimentGUI()
    window.show()
    sys.exit(app.exec())
