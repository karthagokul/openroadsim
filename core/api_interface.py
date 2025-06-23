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

import threading
from core.event_bus import EventBus
from core.plugin_manager import PluginManager
from core.scenario_parser import ScenarioParser
from core.scenario_engine import ScenarioEngine
from core.reporter import Reporter

class APIInterface:
    """
    APIInterface provides a unified programmatic interface for managing the OpenRoadSim simulation workflow.
    It abstracts scenario loading, plugin management, engine execution, and reporting into a thread-based structure
    usable from both console and GUI frontends.

    Attributes:
        logger (Logger): Logger instance for capturing logs.
        plugin_dir (str): Path to plugin directory.
        on_status (callable): Optional callback for status updates (e.g., started, completed).
        on_log (callable): Optional callback for logging simulation messages.
    """

    def __init__(self, logger, plugin_dir="plugins"):
        """
        Initializes the simulation interface and supporting components.

        Args:
            logger (Logger): The logging utility.
            plugin_dir (str): Directory from which to load plugins.
        """
        self.logger = logger
        self.plugin_dir = plugin_dir

        self.event_bus = EventBus(logger)
        self.plugin_manager = PluginManager(logger, self.event_bus, plugin_dir=plugin_dir)
        self.parser = ScenarioParser(logger)
        self.engine = ScenarioEngine(logger, self.event_bus)
        self.reporter = Reporter()

        self.thread = None
        self.running = False
        self.events = []

        self.on_status = None
        self.on_log = None

    def load_scenario(self, scenario_path):
        """
        Parses a YAML scenario file and loads its events.

        Args:
            scenario_path (str): Path to the scenario YAML file.

        Returns:
            bool: True if loading succeeds, raises ValueError otherwise.
        """
        self.events = self.parser.load(scenario_path)
        self.reporter.metadata["scenario_file"] = scenario_path

        if not self.events:
            raise ValueError("No valid events loaded.")

        self._log(f"Loaded {len(self.events)} events from scenario.")
        return True

    def start(self):
        """
        Starts the simulation in a background thread.

        Loads all plugins, then runs the scenario engine in a non-blocking thread.
        """
        if self.running:
            self._log("Simulation already running.")
            return

        self.plugin_manager.load_plugins()
        self._log("Plugins loaded.")

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        """
        Internal method that runs the simulation engine.

        Handles status tracking and plugin lifecycle management.
        """
        self._status("started")
        try:
            self.engine.run(self.events)
            self._status("completed")
        except Exception as e:
            self._status("error")
            self._log(f"Simulation failed: {e}")
        finally:
            self.plugin_manager.shutdown_plugins()
            self.reporter.write_json("report.json")
            self._log("Simulation report written to report.json")
            self.running = False

    def stop(self):
        """
        Stops a running simulation gracefully.
        """
        if self.running:
            self.engine.stop()
            self._status("stopped")
            self._log("Simulation stopped by user.")

    def _log(self, msg):
        """
        Internal helper for logging messages to external listeners or fallback to logger.

        Args:
            msg (str): The message to log.
        """
        if self.on_log:
            self.on_log(msg)
        else:
            self.logger.info(msg)

    def _status(self, code):
        """
        Internal helper for updating simulation status via callback or logger.

        Args:
            code (str): Status code such as 'started', 'completed', 'error', etc.
        """
        if self.on_status:
            self.on_status(code)
        else:
            self.logger.info(f"Status: {code}")
