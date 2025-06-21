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


import argparse
from utils.logger import Logger
from core.event_bus import EventBus
from core.plugin_manager import PluginManager
from core.scenario_parser import ScenarioParser
from core.scenario_engine import ScenarioEngine

def main():
    parser = argparse.ArgumentParser(
        description="OpenRoadSim - Open-source Automotive Signal Simulator"
    )

    parser.add_argument(
        "scenario",
        help="Path to the YAML scenario file to execute"
    )

    parser.add_argument(
        "--plugin-dir",
        default="plugins",
        help="Path to the plugin directory (default: plugins/)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )

    args = parser.parse_args()

    logger = Logger("Main", enable_debug=args.debug)
    logger.info("OpenRoadSim — Phase 1 Starting Up")

    # Load and parse scenario
    parser_engine = ScenarioParser(logger)
    events = parser_engine.load(args.scenario)
    if not events:
        logger.error("No valid events found. Exiting.")
        return

    # Init event bus
    event_bus = EventBus(logger)

    # Load plugins
    plugin_manager = PluginManager(logger, event_bus, plugin_dir=args.plugin_dir)
    plugin_manager.load_plugins()

    # Run scenario
    engine = ScenarioEngine(logger, event_bus)
    try:
        engine.run(events)
    except KeyboardInterrupt:
        logger.warn("Interrupted by user.")
        engine.stop()

    # Shutdown plugins
    plugin_manager.shutdown_plugins()
    logger.info("Simulation complete. Goodbye!")

if __name__ == "__main__":
    main()
