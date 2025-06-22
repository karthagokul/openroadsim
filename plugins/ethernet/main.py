# MIT License
# Copyright (c) 2024 Gokul Kartha
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
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
    """
    EthernetPlugin simulates Ethernet communication for scenarios like
    firmware update transfers over TCP.

    It handles connection management, sending commands to a mock server,
    and manages state transitions for connect, disconnect, transfer start,
    resume, and completion.
    """

    def __init__(self):
        """
        Initialize the EthernetPlugin instance.

        Sets default server IP and port to None and 9000 respectively,
        initializes socket and connection state.
        """
        self.name = "EthernetPlugin"
        self.logger = Logger(self.name)
        self.sock = None
        self.connected = False
        self.server_ip = None
        self.server_port = 9000
        self.active_session = None

    def on_init(self, config):
        """
        Plugin initialization hook called once after loading.

        Args:
            config (dict): Optional configuration dictionary.

        Logs the plugin initialization message.
        """
        self.logger.info("EthernetPlugin initialized.")

    def on_event(self, topic, data, timestamp):
        """
        Called when an event targeted to this plugin is received.

        Args:
            topic (str): Event topic in format '<target>.<action>'.
            data (dict): Event payload data, typically parameters.
            timestamp (float): Simulation timestamp of event in seconds.

        Parses the action from the topic and dispatches it to appropriate
        internal handlers such as connect, disconnect, start_transfer, etc.
        Specially handles resume_transfer by attempting reconnect if disconnected.
        Logs unknown actions as warnings.
        """
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
        """
        Establish a TCP connection to the configured server IP and port.

        Args:
            timestamp (float): Simulation timestamp for logging.
        
        If already connected, logs a warning and returns.
        On success, sets connection state and logs the event.
        On failure, logs the exception.
        """
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
        """
        Close the TCP connection if open and update connection state.

        Args:
            timestamp (float): Simulation timestamp for logging.
        
        Logs disconnection and resets internal socket and state.
        """
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        self.sock = None
        self.connected = False
        self.logger.info(f"[{timestamp:.3f}s] Ethernet disconnected.")

    def _send_message(self, cmd, payload, timestamp):
        """
        Send a JSON-encoded message over the socket.

        Args:
            cmd (str): Command string (e.g., 'start_transfer').
            payload (dict): Data dictionary to send.
            timestamp (float): Simulation timestamp for logging.

        Formats a JSON message, sends it with newline delimiter.
        Logs success or failure, and disconnects on failure.
        """
        message = {"cmd": cmd, "data": payload}
        try:
            self.sock.sendall((json.dumps(message) + "\n").encode())
            self.logger.info(f"[{timestamp:.3f}s] Sent '{cmd}' with data: {payload}")
        except Exception as e:
            self.logger.error(f"[{timestamp:.3f}s] Error sending message: {e}")
            self._disconnect(timestamp)

    def on_shutdown(self):
        """
        Called during plugin shutdown to clean up resources.

        Disconnects the socket and logs the shutdown event.
        """
        self._disconnect(timestamp=0.0)
        self.logger.info("EthernetPlugin shut down.")
