import unittest
from PyQt6.QtWidgets import QApplication
from src.core.mqtt_manager import MqttManager
from src.gui.main_window import MainWindow
from plugins.wavemeter.wavemeter_plugin import WavemeterPlugin
import time

class TestWavemeterSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance if it doesn't exist
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_plugin_loading(self):
        window = MainWindow()
        # Allow some time for plugins to load (though it's synchronous in this implementation)
        self.assertTrue(len(window.plugins) > 0, "No plugins loaded")

        found_wavemeter = False
        for plugin in window.plugins:
            # Check by class name because dynamic loading might cause identity issues in tests
            if type(plugin).__name__ == 'WavemeterPlugin':
                found_wavemeter = True
                break
        self.assertTrue(found_wavemeter, "Wavemeter plugin not found")
        window.mqtt_manager.stop()

    def test_wavemeter_update(self):
        plugin = WavemeterPlugin(num_channels=4)

        # Simulate receiving a message
        test_freq = 123.456
        plugin.handle_message("instruments/wavemeter/channel/1/frequency", str(test_freq))

        # Check if the label updated
        label_text = plugin.channels[1].freq_label.text()
        self.assertEqual(label_text, f"{test_freq:.6f} THz")

        # Test invalid channel
        plugin.handle_message("instruments/wavemeter/channel/99/frequency", "100.0")
        # Should not crash

        # Test invalid payload
        plugin.handle_message("instruments/wavemeter/channel/1/frequency", "invalid")
        # Should not crash, label should remain same
        self.assertEqual(plugin.channels[1].freq_label.text(), f"{test_freq:.6f} THz")

if __name__ == '__main__':
    unittest.main()
