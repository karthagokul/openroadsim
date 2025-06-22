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


from core.base_plugin import BasePlugin
from utils.logger import Logger
import socket
import json

class EthernetPlugin(BasePlugin):
    def __init__(self):
        self.name = "EthernetPlugin"
        self.logger = Logger(self.name)
        self.sock = None
        self.connected = False
        self.server_ip = None
        self.server_port = 9000
        self.active_session = None

    def on_init(self, config):
        self.logger.info("EthernetPlugin initialized.")

    def on_event(self, topic, data, timestamp):
        action = topic.split(".")[-1]
        params = data.get("params", data)

        if action in ["connect", "reconnect"]:
            self.server_ip = params.get("ip")
            self.server_port = params.get("port", self.server_port)
            if not self.server_ip:
                self.logger.error(f"[{timestamp:.3f}s] Missing 'ip' in {action} params.")
                return
            self._connect(timestamp)

        elif action == "disconnect":
            self._disconnect(timestamp)

        elif action == "resume_transfer":
            # Attempt reconnect if not already connected
            if not self.connected:
                ip = params.get("ip", self.server_ip)
                port = params.get("port", self.server_port)
                if ip:
                    self.server_ip = ip
                    self.server_port = port
                    self._connect(timestamp)
                else:
                    self.logger.error(f"[{timestamp:.3f}s] Cannot reconnect — no IP specified.")
                    return

            # Proceed with sending the resume_transfer message
            if self.connected:
                self._send_message(action, params, timestamp)
            else:
                self.logger.warn(f"[{timestamp:.3f}s] Reconnect failed. Cannot perform 'resume_transfer'.")

        elif action in ["start_transfer", "complete_transfer"]:
            if not self.connected:
                self.logger.warn(f"[{timestamp:.3f}s] Not connected. Cannot perform '{action}'.")
                return
            self._send_message(action, params, timestamp)

        else:
            self.logger.warn(f"[{timestamp:.3f}s] Unknown action '{action}'")


    def _connect(self, timestamp):
        if self.connected:
            self.logger.warn(f"[{timestamp:.3f}s] Already connected to {self.server_ip}:{self.server_port}")
            return
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_ip, self.server_port))
            self.connected = True
            self.logger.info(f"[{timestamp:.3f}s] Connected to {self.server_ip}:{self.server_port}")
        except Exception as e:
            self.logger.error(f"[{timestamp:.3f}s] Failed to connect: {e}")

    def _disconnect(self, timestamp):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        self.sock = None
        self.connected = False
        self.logger.info(f"[{timestamp:.3f}s] Ethernet disconnected.")

    def _send_message(self, cmd, payload, timestamp):
        message = {"cmd": cmd, "data": payload}
        try:
            self.sock.sendall((json.dumps(message) + "\n").encode())
            self.logger.info(f"[{timestamp:.3f}s] Sent '{cmd}' with data: {payload}")
        except Exception as e:
            self.logger.error(f"[{timestamp:.3f}s] Error sending message: {e}")
            self._disconnect(timestamp)

    def on_shutdown(self):
        self._disconnect(timestamp=0.0)
        self.logger.info("EthernetPlugin shut down.")
