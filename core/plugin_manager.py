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


import os
import importlib.util
import yaml

class PluginManager:
    """
    PluginManager is responsible for dynamically loading and managing simulation plugins.

    It:
    - Loads plugin metadata from each plugin's `plugin.yaml`
    - Dynamically imports the plugin's main module (`main.py`)
    - Instantiates the plugin class
    - Registers subscriptions with the EventBus
    - Manages lifecycle hooks (init and shutdown)
    """

    def __init__(self, logger, event_bus, plugin_dir="plugins"):
        """
        Initializes the PluginManager.

        Args:
            logger (Logger): The logging utility instance.
            event_bus (EventBus): The event dispatcher used to route plugin events.
            plugin_dir (str): The directory path where plugins are located.
        """
        self.logger = logger
        self.event_bus = event_bus
        self.plugin_dir = plugin_dir
        self.plugins = []

    def load_plugins(self):
        """
        Discovers, loads, and registers all plugins from the plugin directory.

        - Validates that each plugin folder contains `plugin.yaml` and `main.py`.
        - Dynamically imports the plugin class defined in metadata (`entry_class`, defaults to `Plugin`).
        - Calls each plugin's `on_init()` method.
        - Subscribes the plugin to topics defined in `plugin.yaml` (under `subscriptions`).
        """
        self.logger.info(f"Loading plugins from '{self.plugin_dir}'")

        for plugin_name in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, plugin_name)
            if not os.path.isdir(plugin_path):
                continue

            meta_path = os.path.join(plugin_path, "plugin.yaml")
            code_path = os.path.join(plugin_path, "main.py")

            if not os.path.exists(meta_path) or not os.path.exists(code_path):
                self.logger.warn(f"Skipping plugin '{plugin_name}' (missing plugin.yaml or main.py)")
                continue

            try:
                with open(meta_path, 'r') as f:
                    metadata = yaml.safe_load(f)

                # Dynamic import of the plugin's main class
                spec = importlib.util.spec_from_file_location(f"{plugin_name}.main", code_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                plugin_class = getattr(module, metadata.get("entry_class", "Plugin"))
                plugin_instance = plugin_class()
                plugin_instance.name = metadata.get("name", plugin_name)

                # Register plugin subscriptions to EventBus
                for sub in metadata.get("subscriptions", []):
                    target = sub.get("target")
                    actions = sub.get("actions", [])
                    for action in actions:
                        topic = f"{target}.{action}"
                        if target == "*" and action == "*":
                            topic = "*"  # Special case: full wildcard
                        self.event_bus.subscribe(topic, plugin_instance)

                self.plugins.append(plugin_instance)
                plugin_instance.on_init({})
                self.logger.info(f"Loaded plugin '{plugin_instance.name}'")

            except Exception as e:
                self.logger.error(f"Failed to load plugin '{plugin_name}': {e}")

    def shutdown_plugins(self):
        """
        Gracefully shuts down all loaded plugins by calling their `on_shutdown()` methods.
        Logs any failures during shutdown.
        """
        for plugin in self.plugins:
            try:
                plugin.on_shutdown()
            except Exception as e:
                self.logger.warn(f"Plugin '{plugin.name}' failed to shut down cleanly: {e}")
