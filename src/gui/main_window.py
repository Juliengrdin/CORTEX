import sys
import os
import importlib.util
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QMessageBox
from src.core.mqtt_manager import MqttManager
from src.core.plugin_interface import InstrumentPlugin

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modular Lab Control System")
        self.resize(1024, 768)

        # Central Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Tab Widget for Plugins
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # MQTT Manager
        self.mqtt_manager = MqttManager()
        self.mqtt_manager.message_received.connect(self.dispatch_message)
        self.mqtt_manager.start()

        self.plugins = []
        self.load_plugins()

    def load_plugins(self):
        """
        Dynamically loads plugins from the 'plugins' directory.
        """
        plugins_dir = os.path.join(os.getcwd(), 'plugins')
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir)
            print(f"Created plugins directory at {plugins_dir}")
            return

        for root, dirs, files in os.walk(plugins_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    filepath = os.path.join(root, file)
                    self.load_plugin_from_file(filepath)

    def load_plugin_from_file(self, filepath):
        try:
            spec = importlib.util.spec_from_file_location("module.name", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find subclasses of InstrumentPlugin
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type) and \
                   issubclass(attribute, InstrumentPlugin) and \
                   attribute is not InstrumentPlugin:

                    # Instantiate the plugin
                    plugin_instance = attribute()
                    self.add_plugin(plugin_instance, attribute_name)
                    print(f"Loaded plugin: {attribute_name}")
        except Exception as e:
            print(f"Failed to load plugin from {filepath}: {e}")

    def add_plugin(self, plugin, name):
        self.plugins.append(plugin)
        self.tabs.addTab(plugin, name)

        # Subscribe to plugin topics
        topics = plugin.get_subscribe_topics()
        for topic in topics:
            self.mqtt_manager.subscribe(topic)

    def dispatch_message(self, topic, payload):
        """
        Dispatches MQTT messages to relevant plugins.
        """
        for plugin in self.plugins:
            # Simple topic matching (could be improved with wildcards)
            # Assuming plugins want to handle messages for topics they subscribed to.
            # But the MQTT manager emits all messages.
            # We can let the plugin filter or check if the topic matches any of its subscriptions.

            # For this implementation, we pass everything to the plugin and let it decide,
            # or check if it matches subscribed topics (accounting for wildcards is tricky without a library)

            # Since InstrumentPlugin has handle_message, we just call it.
            plugin.handle_message(topic, payload)

    def closeEvent(self, event):
        self.mqtt_manager.stop()
        super().closeEvent(event)
