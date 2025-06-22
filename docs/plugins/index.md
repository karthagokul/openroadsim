# Plugin APIs

Explore available simulation plugins in OpenRoadSim.

- [CAN Plugin](can.md)
- [Echo Plugin](echo.md)
- [GPS Plugin](gps.md)
- [Media Plugin](media.md)
- [Replay GPS Plugin](replay_gps.md)
- [Ethernet Plugin](ethernet.md)


## OpenRoadSim Plugin Development Guide

### Overview

OpenRoadSim plugins extend the core simulation by implementing specific protocol or subsystem behavior (e.g., CAN, GPS, Ethernet). Plugins subscribe to events, process them, and emit new events or logs as needed.


### Plugin Structure

-   Each plugin is a Python class derived from `core.base_plugin.BasePlugin`.
    
-   Must implement lifecycle methods: `on_init()`, `on_event()`, and `on_shutdown()`.
    
-   Has a `Logger` for colored logging.
    
-   Packaged with a `plugin.yaml` metadata file for discovery.

#### Folder Layout Example

    openroadsim/
    └── plugins/
        └── MyPlugin/
            ├── MyPlugin.py
            └── plugin.yaml

### Step 1: Create the Plugin Class

    from core.base_plugin import BasePlugin
    from utils.logger import Logger
    
    class Plugin(BasePlugin):
        def __init__(self):
            self.name = "MyPlugin"
            self.logger = Logger(self.name)
        
        def on_init(self, config):
            # Called once when plugin is initialized
            self.logger.info("Plugin initialized")
        
        def on_event(self, topic, data, timestamp):
            # Called for each matching event
            self.logger.info(f"Event {topic} received at {timestamp}s with data {data}")
            # Process event here...
        
        def on_shutdown(self):
            # Cleanup before plugin unload
            self.logger.info("Plugin shutting down")


### Step 2: Create `plugin.yaml`

       name: MyPlugin
        entry_class: Plugin
        subscriptions:
          - target: <target-name>
            actions: ["action1", "action2", "*"]

-   **`name`**: Plugin display name.    
-   **`entry_class`**: Python class name (usually `Plugin`).    
-   **`subscriptions`**: List of event subscriptions by target and action.

### Step 3: Event Subscription & Handling

-   Plugins receive only events matching their subscriptions.    
-   `on_event` arguments:  
    -   `topic` (string): `"<target>.<action>"` format.        
    -   `data` (dict): Event payload (parameters).        
    -   `timestamp` (float): Simulation time in seconds.        
-   Parse `topic` to extract `target` and `action`.    
-   Process data and optionally emit logs, events, or manipulate state.

### Step 4: Logging

Use the provided `Logger` class for colored logs:

    self.logger.info("Info message")     # Blue
    self.logger.warn("Warning message")  # Yellow
    self.logger.error("Error message")   # Red
    self.logger.debug("Debug message")   # Gray (enable debug in config)

### Step 5: Plugin Lifecycle

`on_init` | At plugin load time |   Initialize state and resources
`on_event`  | When subscribed events occur |  Handle simulation events
`on_shutdown` |  When simulation ends or plugin unloads  | Cleanup, close connections, free resources

### Step 6: Testing Your Plugin

-   Place your plugin folder inside `plugins/`.
    
-   Create a scenario YAML triggering your target/actions.
    
-   Run & Observe logs and behavior.
`python main.py scenarios/your_scenario.yaml`


### Tips

-   Keep plugins focused on one subsystem or protocol.     
-   Use `self.logger` extensively for debugging.    
-   Handle exceptions gracefully inside `on_event`.    
-   Use your plugin to emit new events if needed (via EventBus, future versions).    
-   Start simple; iterate based on scenario needs.