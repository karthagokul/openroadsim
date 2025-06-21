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


from sdk.base_plugin import BasePlugin
from utils.logger import Logger

class Plugin(BasePlugin):
    """
    Simulates GPS location updates and signal loss.
    """
    def __init__(self):
        self.name = "GPSPlugin"
        self.logger = Logger(self.name)
        self.active = True
        self.location = {"lat": 0.0, "lon": 0.0}

    def on_init(self, config):
        self.logger.info("GPS plugin initialized.")

    def on_event(self, topic, data, timestamp):
        action = topic.split(".")[1]

        if action == "set_location":
            lat = data.get("lat")
            lon = data.get("lon")
            if lat is not None and lon is not None:
                self.location = {"lat": lat, "lon": lon}
                self.active = True
                self.logger.info(f"[{timestamp:.3f}s] GPS location set to ({lat}, {lon})")
            else:
                self.logger.warn(f"Invalid location data: {data}")

        elif action == "simulate_loss":
            self.active = False
            self.logger.info(f"[{timestamp:.3f}s] GPS signal lost.")

    def on_shutdown(self):
        self.logger.info("GPS plugin shutting down.")

