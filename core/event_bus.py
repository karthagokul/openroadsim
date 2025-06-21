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


class EventBus:
    """
    EventBus is the central messaging system for OpenRoadSim.
    It handles publishing and subscribing of events between the ScenarioEngine and plugins.

    Events are routed based on a topic string in the form 'target.action'
    (e.g., 'can.send', 'gps.update').
    """

    def __init__(self, logger):
        """
        Initializes the EventBus.

        Args:
            logger (Logger): An instance of the project's logger to output debug/info messages.
        """
        self.logger = logger
        self.subscriptions = {}  # Maps topic (str) to a list of plugin instances

    def subscribe(self, topic, plugin):
        """
        Subscribes a plugin to a specific event topic.

        Args:
            topic (str): The event topic to listen for (e.g., "echo.say").
            plugin (BasePlugin): An instance of a plugin that implements on_event().
        """
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(plugin)
        self.logger.debug(f"{plugin.name} subscribed to {topic}")

    def publish(self, topic, data, timestamp):
        """
        Publishes an event to all plugins subscribed to the given topic.

        Args:
            topic (str): The event topic to publish (e.g., "gps.set_location").
            data (dict): A dictionary of parameters for the event.
            timestamp (float): Simulation time at which the event occurs.
        """
        if topic not in self.subscriptions:
            self.logger.warn(f"No subscribers for topic: {topic}")
            return

        for plugin in self.subscriptions[topic]:
            try:
                plugin.on_event(topic, data, timestamp)
            except Exception as e:
                self.logger.error(f"Plugin '{plugin.name}' failed on {topic}: {e}")
