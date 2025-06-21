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
import time
import json

class Reporter:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.metadata = {
                "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "plugins": [],
                "scenario_file": "",
            }
            self.event_log = []
            self.plugin_responses = []
            self.errors = []

    def _now(self):
        return {
            "real_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "real_timestamp": time.time()
        }

    def log_event(self, topic, data, sim_time):
        entry = {
            "topic": topic,
            "data": data,
            "sim_time": sim_time
        }
        entry.update(self._now())
        self.event_log.append(entry)

    def log_plugin_response(self, plugin, topic, response, sim_time):
        entry = {
            "plugin": plugin,
            "topic": topic,
            "response": str(response),
            "sim_time": sim_time
        }
        entry.update(self._now())
        self.plugin_responses.append(entry)

    def log_error(self, plugin, topic, error):
        entry = {
            "plugin": plugin,
            "topic": topic,
            "error": str(error)
        }
        entry.update(self._now())
        self.errors.append(entry)

    def write_json(self, path="report.json"):
        with open(path, "w") as f:
            json.dump({
                "metadata": self.metadata,
                "events": self.event_log,
                "responses": self.plugin_responses,
                "errors": self.errors
            }, f, indent=2)
