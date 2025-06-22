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
import time
from core.base_plugin import BasePlugin
from utils.logger import Logger

class ReplayGPSPlugin(BasePlugin):
    """
    Replays GPS coordinates from a NMEA log and emits gps.set_location events.
    """

    def __init__(self):
        self.name = "ReplayGPSPlugin"
        self.logger = Logger(self.name)
        self.thread = None
        self.running = False
        self.event_bus = None  # Will be injected externally

    def on_init(self, config):
        self.logger.info("ReplayGPSPlugin initialized.")

    def on_event(self, topic, data, scenario_timestamp):
        if topic.endswith("start_replay"):
            file = data.get("file")
            speed = float(data.get("speed", 1.0))
            if file:
                self.thread = threading.Thread(
                    target=self._replay_file,
                    args=(file, speed, scenario_timestamp),
                    daemon=True
                )
                self.running = True
                self.thread.start()
                self.thread.join()
            else:
                self.logger.error("Missing 'file' parameter for start_replay.")

    def _replay_file(self, filepath, speed, scenario_start_time):
        self.logger.info(f"Replaying GPS from {filepath} at {speed}x speed")

        try:
            with open(filepath, 'r') as f:
                base_nmea_time = None
                sim_time = scenario_start_time

                for line in f:
                    if not self.running:
                        break

                    if line.startswith('$GPGGA'):
                        parts = line.strip().split(',')

                        # Parse NMEA time (HHMMSS.sss)
                        nmea_raw = parts[1]
                        if not nmea_raw:
                            continue
                        hh = int(nmea_raw[0:2])
                        mm = int(nmea_raw[2:4])
                        ss = float(nmea_raw[4:])
                        nmea_seconds = hh * 3600 + mm * 60 + ss

                        if base_nmea_time is None:
                            base_nmea_time = nmea_seconds
                            offset = 0.0
                        else:
                            offset = (nmea_seconds - base_nmea_time) / speed

                        sim_time = scenario_start_time + offset

                        lat, lon = self._parse_nmea(parts)
                        if lat is not None and lon is not None:
                            self._emit_gps(lat, lon, sim_time)
                            time.sleep(0.05)  # keep CPU cool

        except Exception as e:
            self.logger.error(f"Replay failed: {e}")

    def _emit_gps(self, lat, lon, sim_time):
        event = {
            "lat": lat,
            "lon": lon
        }
        self.event_bus.publish("gps.set_location", event, sim_time)

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
        deg_len = 2 if len(coord.split('.')[0]) <= 4 else 3
        degrees = int(coord[:deg_len])
        minutes = float(coord[deg_len:])
        decimal = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal

    def on_shutdown(self):
        self.logger.info("ReplayGPSPlugin shutting down.")
        self.running = False
