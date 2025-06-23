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
    Singleton class providing a unified API for managing OpenRoadSim simulation lifecycle.

    This class encapsulates scenario parsing, plugin management, engine execution, and result reporting.
    It is designed for use by both GUI and console tools.

    Example usage:
        from core.api_interface import APIInterface
        api = APIInterface.get_instance(logger)
        api.load_scenario("scenarios/example.yaml")
        api.start()

    Attributes:
        logger (Logger): Logger used for output.
        plugin_dir (str): Plugin folder path (defaults to 'plugins').
        on_status (callable): Optional callback for simulation status events.
        on_log (callable): Optional callback for simulation log messages.
    """

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, logger=None, plugin_dir="plugins"):
        """
        Retrieves the global singleton instance.

        Args:
            logger (Logger): Logger instance (required on first call).
            plugin_dir (str): Optional path to plugins folder.

        Returns:
            APIInterface: Shared instance of the APIInterface.
        """
        with cls._lock:
            if cls._instance is None:
                if logger is None:
                    raise ValueError("Logger must be provided for first initialization.")
                cls._instance = cls(logger, plugin_dir)
        return cls._instance

    def __init__(self, logger, plugin_dir="plugins"):
        if hasattr(self, "_initialized") and self._initialized:
            return  # prevent reinitialization

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

        self._initialized = True

    def load_scenario(self, scenario_path):
        """
        Parses a YAML scenario file and prepares its events for execution.

        Args:
            scenario_path (str): Path to the scenario YAML file.

        Returns:
            bool: True if the scenario was successfully loaded.

        Raises:
            ValueError: If no events are found in the scenario.
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

        Loads plugins, begins execution of scenario events, and monitors progress.
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
        Executes the simulation engine.

        Manages status callbacks and handles errors and cleanup.
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
        Gracefully stops the currently running simulation.
        """
        if self.running:
            self.engine.stop()
            self._status("stopped")
            self._log("Simulation stopped by user.")

    def _log(self, msg):
        """
        Emits a log message through the registered callback or logger.

        Args:
            msg (str): Log content.
        """
        if self.on_log:
            self.on_log(msg)
        else:
            self.logger.info(msg)

    def _status(self, code):
        """
        Emits a status update through the registered callback or logger.

        Args:
            code (str): One of: 'started', 'completed', 'stopped', or 'error'.
        """
        if self.on_status:
            self.on_status(code)
        else:
            self.logger.info(f"Status: {code}")
