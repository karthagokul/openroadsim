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


import time

class ScenarioEngine:
    """
    ScenarioEngine is responsible for orchestrating the execution of simulation events
    according to their scheduled timestamps.

    It reads a list of parsed scenario events and dispatches them via the EventBus
    to subscribed plugins in time-aligned order.
    """

    def __init__(self, logger, event_bus):
        """
        Initializes the ScenarioEngine.

        Args:
            logger (Logger): Logger instance for outputting status and debug info.
            event_bus (EventBus): Event bus for publishing events to plugins.
        """
        self.logger = logger
        self.event_bus = event_bus
        self.running = False

    def run(self, events):
        """
        Executes a scenario by processing each event at its designated simulation time.

        This function uses real wall-clock time to delay dispatch until the scheduled `event['time']`.

        Args:
            events (list[dict]): List of events loaded from a scenario file.
                                 Each event must include 'time', 'target', 'action', and optional 'params'.
        """
        self.logger.info(f"Starting scenario with {len(events)} event(s).")
        self.running = True
        start_time = time.time()

        for event in events:
            if not self.running:
                self.logger.warn("Scenario stopped prematurely.")
                break

            event_time = float(event["time"])
            now = time.time()
            elapsed = now - start_time
            wait_time = max(0, event_time - elapsed)

            if wait_time > 0:
                time.sleep(wait_time)

            topic = f"{event['target']}.{event['action']}"
            params = event.get("params", {})

            self.logger.debug(f"Dispatching event @ {event_time:.3f}s → {topic}")
            self.event_bus.publish(topic, params, event_time)

        self.logger.info("Scenario completed.")

    def stop(self):
        """
        Stops the currently running scenario (typically via user interrupt).
        """
        self.logger.warn("Stopping scenario execution.")
        self.running = False
