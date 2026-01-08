from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget

class InstrumentPlugin(QWidget):
    """
    Abstract base class for all instrument plugins.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def get_subscribe_topics(self) -> list[str]:
        """
        Returns a list of MQTT topics this plugin needs to subscribe to.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Plugins must implement get_subscribe_topics")

    def handle_message(self, topic: str, payload: str):
        """
        Handles incoming MQTT messages for subscribed topics.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Plugins must implement handle_message")
