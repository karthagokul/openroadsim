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
from constants import GUI_LOGGER

class LogConsoleWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumBlockCount(1000)
        
        # Register the widget's log appender as a global listener
        GUI_LOGGER.add_global_listener(self.append_log)
        GUI_LOGGER.info("Log Widget is created.")

        # Optional: monospaced font
        self.setStyleSheet("font-family: Consolas, monospace; font-size: 11pt;")

    def append_log(self, level, name, message, timestamp):
        """
        Appends a log message to the console with appropriate color formatting.

        Args:
            level (str): Log level (INFO, WARN, ERROR, DEBUG).
            name (str): Source name or tag of the logger.
            message (str): Log message content.
            timestamp (str): Time the log was generated.
        """
        line = f"[{timestamp}] [{name}] [{level}] {message}"

        self.appendPlainText(line)
        self.moveCursor(QTextCursor.End)
