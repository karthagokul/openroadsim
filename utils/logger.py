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

import sys
import datetime

class Logger:
    """
    Logger is a minimal, extensible logging utility with real-time broadcasting support.

    It supports:
    - INFO, WARN, ERROR, DEBUG log levels
    - Custom listeners per instance or globally
    - Timestamped log dispatching without printing directly to stdout
    - Debug filtering controlled by the constructor flag

    Listeners can be used to pipe logs to GUIs, files, or consoles with color formatting.
    """

    _global_listeners = []  # Shared across all Logger instances

    def __init__(self, name='ORS', enable_debug=False):
        """
        Initialize a Logger instance.

        Args:
            name (str): Logical name for the logger (e.g., module or plugin name).
            enable_debug (bool): Whether DEBUG messages should be emitted.
        """
        self.name = name
        self.enable_debug = enable_debug
        self.listeners = list(Logger._global_listeners)  # Copy current global listeners

    @classmethod
    def add_global_listener(cls, listener_func):
        """
        Registers a listener that receives logs from *all* Logger instances, current and future.

        Args:
            listener_func (function): Callable with signature (level, name, message, timestamp).
        """
        cls._global_listeners.append(listener_func)

    def add_listener(self, listener_func):
        """
        Adds a listener for this specific logger instance.

        Args:
            listener_func (function): Callable with signature (level, name, message, timestamp).
        """
        self.listeners.append(listener_func)

    def remove_listener(self, listener_func):
        """
        Removes a previously added listener from this logger instance.

        Args:
            listener_func (function): The listener function to remove.
        """
        if listener_func in self.listeners:
            self.listeners.remove(listener_func)

    def _notify(self, level, message, timestamp):
        """
        Internal method to dispatch log messages to all registered listeners.

        Args:
            level (str): Log level (INFO, WARN, ERROR, DEBUG).
            message (str): The message to emit.
            timestamp (str): Formatted time string (e.g., "12:34:56").
        """
        for listener in self.listeners:
            try:
                listener(level, self.name, message, timestamp)
            except Exception as e:
                print(f"[Logger:{self.name}] Listener error: {e}", file=sys.stderr)

        #Case especially for GUI app :  notify global listeners directly (even if added after this logger was created)
        for global_listener in Logger._global_listeners:
            if global_listener not in self.listeners:
                try:
                    global_listener(level, self.name, message, timestamp)
                except Exception as e:
                    print(f"[Logger:{self.name}] Global listener error: {e}", file=sys.stderr)

    def _log(self, level, message):
        """
        Internal method to process a log event and notify listeners if allowed by debug filter.

        Args:
            level (str): Log level.
            message (str): Log message content.
        """
        if level == 'DEBUG' and not self.enable_debug:
            return

        now = datetime.datetime.now().strftime('%H:%M:%S')
        #print(message) #enable this to debug logging issues(?)
        self._notify(level, message, now)

    def info(self, message):
        """Log an INFO-level message."""
        self._log('INFO', message)

    def warn(self, message):
        """Log a WARN-level message."""
        self._log('WARN', message)

    def error(self, message):
        """Log an ERROR-level message."""
        self._log('ERROR', message)

    def debug(self, message):
        """Log a DEBUG-level message (only if enabled)."""
        self._log('DEBUG', message)
