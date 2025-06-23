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

from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtCore import QTimer
from constants import GUI_LOGGER
import queue


class LogConsoleWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumBlockCount(1000)

        # Optional: monospaced font
        self.setStyleSheet("font-family: Consolas, monospace; font-size: 11pt;")

        # Internal log queue to avoid cross-thread crashes
        self.log_queue = queue.Queue()

        # Register the widget's log appender as a global listener
        GUI_LOGGER.add_global_listener(self._enqueue_log)

        # Timer to periodically process the queue
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._process_log_queue)
        self.timer.start(50)  # every 50ms

    def _enqueue_log(self, level, name, message, timestamp):
        """
        Called by logger; pushes logs into the internal queue.
        """
        self.log_queue.put((level, name, message, timestamp))
        #print(f"[QUEUE] [{timestamp}] [{name}] [{level}] {message}") #Just for testing  , Dont overdo this :)

    def _process_log_queue(self):
        """
        Processes log messages from the queue and appends them to the UI.
        """
        while not self.log_queue.empty():
            try:
                level, name, message, timestamp = self.log_queue.get_nowait()
                self._append_log(level, name, message, timestamp)
            except Exception as e:
                print(f"Log UI queue error: {e}")

    def _append_log(self, level, name, message, timestamp):
        """
        Formats and displays the log message in the text widget.
        """
        
        line = f"[{timestamp}] [{name}] [{level}] {message}"
        self.appendPlainText(line)
        self.moveCursor(QTextCursor.End)
