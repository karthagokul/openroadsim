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


import yaml
import os

class ScenarioParser:
    """
    ScenarioParser is responsible for reading YAML scenario files and converting them
    into a list of executable event dictionaries.

    It supports:
    - Basic event steps with time, target, and action
    - Looping blocks to repeat steps with offsets
    - Variable injection (for future use)
    - Modular scenario imports
    """

    def __init__(self, logger):
        """
        Initializes the parser with a logger.

        Args:
            logger (Logger): The logger instance used for output.
        """
        self.logger = logger
        self.variables = {}

    def load(self, path):
        """
        Loads and parses a scenario YAML file from disk.

        Args:
            path (str): Path to the scenario file.

        Returns:
            list[dict]: A sorted list of events (each with 'time', 'target', 'action', etc.)
        """
        try:
            with open(path, 'r') as f:
                raw_data = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load scenario file: {e}")
            return []

        if isinstance(raw_data, dict) and 'import' in raw_data:
            return self._handle_imports(raw_data, os.path.dirname(path))

        # New: handle top-level keys like 'variables' and 'events'
        if isinstance(raw_data, dict):
            if 'variables' in raw_data:
                self._parse_variables(raw_data['variables'])
            if 'events' in raw_data:
                return self._parse_steps(raw_data['events'])

            self.logger.warn("Scenario YAML missing 'events' key.")
            return []

        return self._parse_steps(raw_data)

    def _parse_steps(self, steps):
        """
        Parses the scenario steps into a normalized list of events.

        Args:
            steps (list): List of raw YAML entries.

        Returns:
            list[dict]: Parsed and time-sorted list of events.
        """
        parsed = []
        for i, step in enumerate(steps):
            if 'loop' in step:
                parsed.extend(self._parse_loop(step['loop']))
            elif 'variables' in step:
                self._parse_variables(step['variables'])
            else:
                event = self._normalize_step(step, i)
                if event:
                    parsed.append(event)
        return sorted(parsed, key=lambda e: e["time"])

    def _normalize_step(self, step, index):
        """
        Ensures a step contains the required fields and formats it into a clean event.

        Args:
            step (dict): A raw YAML event step.
            index (int or str): Line or loop identifier for error reporting.

        Returns:
            dict or None: A valid event dict, or None if invalid.
        """
        required_keys = ("time", "target", "action")
        if not all(k in step for k in required_keys):
            self.logger.warn(f"Skipping invalid step at index {index}: {step}")
            return None

        return {
            "time": float(step["time"]),
            "target": step["target"],
            "action": step["action"],
            "params": step.get("params", {}),
            "condition": step.get("condition", None)
        }

    def _parse_loop(self, loop):
        """
        Handles looped steps and unrolls them into repeated time-offset events.

        Args:
            loop (dict): A loop block with count, interval, and steps.

        Returns:
            list[dict]: Flattened list of events.
        """
        count = loop.get("count", 1)
        interval = loop.get("interval", 1)
        steps = loop.get("steps", [])
        events = []

        for i in range(count):
            offset = i * interval
            for step in steps:
                new_step = step.copy()
                new_step["time"] = float(step.get("time", 0)) + offset
                events.append(self._normalize_step(new_step, f"loop-{i}"))
        return events

    def _parse_variables(self, var_block):
        """
        Stores reusable variables for future parameter expansion.

        Args:
            var_block (dict): A dictionary of reusable variable blocks.
        """
        self.variables.update(var_block)
        self.logger.debug(f"Loaded variables: {self.variables}")

    def _handle_imports(self, data, base_dir):
        """
        Handles imported YAML fragments by path and loads them recursively.

        Args:
            data (dict): YAML data that includes an 'import' directive.
            base_dir (str): Base path to resolve relative imports.

        Returns:
            list[dict]: Events loaded from the imported scenario.
        """
        import_path = data['import']
        if not import_path.endswith(".yaml"):
            import_path += ".yaml"
        full_path = os.path.join(base_dir, import_path)

        self.logger.info(f"Importing scenario: {full_path}")
        return self.load(full_path)
