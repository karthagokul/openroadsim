#
# MIT License
# Copyright (c) 2024 Gokul Kartha <kartha.gokul@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from core.base_plugin import BasePlugin
from utils.logger import Logger

class Plugin(BasePlugin):
    """
    EchoPlugin is a simple diagnostic plugin that echoes incoming events.

    It is useful for testing the event system and verifying that events are
    being dispatched correctly with their data payload and timestamp.
    """

    def __init__(self):
        """
        Initializes the EchoPlugin.

        Sets the plugin name and creates a logger instance.
        """
        self.name = "EchoPlugin"
        self.logger = Logger(self.name)

    def on_init(self, config):
        """
        Called once when the plugin is initialized.

        Args:
            config (dict): Optional configuration parameters (unused in this plugin).
        """
        self.logger.info("Initialized.")

    def on_event(self, topic, data, timestamp):
        """
        Handles incoming events and logs the message.

        If a `message` key exists in the event data, it is echoed.
        Otherwise, the entire data dictionary is converted to a string and echoed.

        Args:
            topic (str): The topic name of the event (e.g., "echo").
            data (dict): Event data payload.
            timestamp (float): Simulation time in seconds when the event occurred.
        """
        message = data.get("message", None)
        if message is None:
            message = str(data)  # Fallback to full data dict
        self.logger.info(f"[{timestamp:.3f}s] Echoed: {message}")

    def on_shutdown(self):
        """
        Called when the plugin is being shut down.

        Used to perform any cleanup before unloading the plugin.
        """
        self.logger.info("Shutting down.")
