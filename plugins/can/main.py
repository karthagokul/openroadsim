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
import can
from core.base_plugin import BasePlugin
from utils.logger import Logger
from core.config_loader import ConfigLoader

class Plugin(BasePlugin):
    def __init__(self):
        self.name = "CanPlugin"
        self.logger = Logger(self.name)
        self.bus = None

    def on_init(self, config):
        plugin_config = ConfigLoader.get("can")
        interface = plugin_config.get("interface")

        if not interface:
            self.logger.error("Missing 'interface' in CAN plugin configuration. Please set can.interface in config.yaml.")
            self.bus = None
            return

        try:
            self.bus = can.interface.Bus(channel=interface, bustype="socketcan")
            self.logger.info(f"CanPlugin initialized on interface: {interface}")
        except Exception as e:
            self.logger.error(f"Failed to initialize SocketCAN on '{interface}': {e}")
            self.bus = None

    def on_event(self, topic, data, timestamp):
        id = data.get("id")

        if id is None:
            self.logger.warn(f"[{timestamp:.3f}s] Missing CAN 'id' in event: {data}")
            return

        if isinstance(id, str) and id.startswith("0x"):
            try:
                id = int(id, 16)
            except ValueError:
                self.logger.warn(f"[{timestamp:.3f}s] Invalid hex ID: {id}")
                return

        if not isinstance(id, int):
            self.logger.warn(f"[{timestamp:.3f}s] CAN ID must be an int, got {type(id).__name__}: {id}")
            return

        value = data.get("data", [])
        hex_data = [f"0x{byte:02X}" for byte in value] if isinstance(value, list) else value
        self.logger.info(f"[{timestamp:.3f}s] Injected CAN ID=0x{id:X}, Data={hex_data}")

        if self.bus and isinstance(value, list):
            try:
                msg = can.Message(arbitration_id=id, data=bytearray(value), is_extended_id=False)
                self.bus.send(msg)
                self.logger.debug(f"Sent to SocketCAN: {msg}")
            except Exception as e:
                self.logger.error(f"Failed to send CAN frame: {e}")

    def on_shutdown(self):
        self.logger.info("CanPlugin shutting down.")
        if self.bus:
            self.bus.shutdown()

