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


class BasePlugin:
    """
    BasePlugin defines the required interface for all OpenRoadSim plugins.

    Every plugin must inherit from this class and implement the following lifecycle methods:
    - on_init(): Called once at startup for initialization.
    - on_event(): Called when a subscribed event is published.
    - on_shutdown(): Called when the simulation ends.
    """

    def on_init(self, config):
        """
        Called once after the plugin is loaded.

        Args:
            config (dict): Optional configuration data (reserved for future use).
        """
        raise NotImplementedError("Plugin must implement on_init()")

    def on_event(self, topic, data, timestamp):
        """
        Called when a relevant event is published on the EventBus.

        Args:
            topic (str): The topic of the event (e.g., "gps.set_location").
            data (dict): Parameters passed with the event.
            timestamp (float): The simulation time when the event is triggered.
        """
        raise NotImplementedError("Plugin must implement on_event()")

    def on_shutdown(self):
        """
        Called once at the end of the simulation to clean up resources.
        """
        raise NotImplementedError("Plugin must implement on_shutdown()")
