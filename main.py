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
from utils.logger import Logger
from core.api_interface import APIInterface
import argparse
import time

# Add colored listener
def color_console_listener(level, tag, message, timestamp):
    COLORS = {
        'INFO': '\033[92m',
        'WARN': '\033[93m',
        'ERROR': '\033[91m',
        'DEBUG': '\033[90m',
        'RESET': '\033[0m',
    }
    color = COLORS.get(level, '')
    reset = COLORS['RESET']
    print(f"{color}[{timestamp}] [{tag}] [{level}] {message}{reset}")

def main():
    parser = argparse.ArgumentParser(description="OpenRoadSim Console Runner")
    parser.add_argument("scenario", help="Path to YAML scenario file")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    Logger.add_global_listener(color_console_listener)
    logger = Logger(enable_debug=args.debug)

    runner = APIInterface.get_instance(logger)

    # These will be echoed again by the listener
    runner.on_log = lambda msg: logger.info(msg)
    runner.on_status = lambda code: logger.info(f"[Status] {code}")

    try:
        runner.load_scenario(args.scenario)
        runner.start()

        # Wait for completion
        while runner.running:
            time.sleep(0.5)

    except Exception as e:
        logger.error(f"Error: {e}")

    logger.info("Simulation done.")

if __name__ == "__main__":
    main()
