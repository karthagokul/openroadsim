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

#
# MIT License
# Copyright (c) 2024 Gokul Kartha
#

import threading
import time
from sdk.base_plugin import BasePlugin
from utils.logger import Logger

class Plugin(BasePlugin):
    """
    Replays GPS coordinates from a GPX or NMEA log and emits gps.set_location events.
    """

    def __init__(self):
        self.name = "ReplayGPSPlugin"
        self.logger = Logger(self.name)
        self.thread = None
        self.running = False
        self.event_bus = None  # We'll inject this at on_init

    def on_init(self, config):
        self.logger.info("ReplayGPSPlugin initialized.")

    def on_event(self, topic, data, timestamp):
        if topic.endswith("start_replay"):
            file = data.get("file")
            speed = float(data.get("speed", 1.0))
            if file:
                self.thread = threading.Thread(target=self._replay_file, args=(file, speed), daemon=True)
                self.running = True
                self.thread.start()
                self.thread.join() 
            else:
                self.logger.error("Missing 'file' parameter for start_replay.")

    def _replay_file(self, filepath, speed):
        self.logger.info(f"Replaying GPS from {filepath} at {speed}x speed")

        try:
            with open(filepath, 'r') as f:
                last_time = None
                for line in f:
                    if not self.running:
                        break

                    if line.startswith('$GPRMC') or line.startswith('$GPGGA'):
                        parts = line.split(',')
                        try:
                            lat, lon = self._parse_nmea(parts)
                            if lat is not None and lon is not None:
                                now = time.time()
                                if last_time:
                                    delta = now - last_time
                                    time.sleep(max(0, delta / speed))
                                last_time = now
                                self._emit_gps(lat, lon)
                        except Exception as e:
                            continue
        except Exception as e:
            self.logger.error(f"Replay failed: {e}")

    def _emit_gps(self, lat, lon):
        event = {
            "lat": lat,
            "lon": lon
        }
        self.event_bus.publish("gps.set_location", event, time.time())

    def _parse_nmea(self, parts):
        try:
            lat_raw = parts[2]
            lat_dir = parts[3]
            lon_raw = parts[4]
            lon_dir = parts[5]

            lat = self._convert_to_decimal(lat_raw, lat_dir)
            lon = self._convert_to_decimal(lon_raw, lon_dir)
            return lat, lon
        except:
            return None, None

    def _convert_to_decimal(self, coord, direction):
        if not coord:
            return None
        degrees = int(coord[:2])
        minutes = float(coord[2:])
        decimal = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal

    def on_shutdown(self):
        self.logger.info("ReplayGPSPlugin shutting down.")
        self.running = False
