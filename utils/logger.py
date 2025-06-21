#
# MIT License
#
# Copyright (c) 2024 Gokul Kartha
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

# Author: Gokul Kartha <kartha.gokul@gmail.com>
# File: logger.py
# Description: App Logger Class


import sys
import datetime

class Logger:
    COLORS = {
        'INFO': '\033[94m',     # Blue
        'WARN': '\033[93m',     # Yellow
        'ERROR': '\033[91m',    # Red
        'DEBUG': '\033[90m',    # Gray
        'RESET': '\033[0m'
    }

    def __init__(self, name='Core', enable_debug=False):
        self.name = name
        self.enable_debug = enable_debug

    def _log(self, level, message):
        if level == 'DEBUG' and not self.enable_debug:
            return
        now = datetime.datetime.now().strftime('%H:%M:%S')
        color = self.COLORS.get(level, '')
        reset = self.COLORS['RESET']
        print(f"{color}[{now}] [{self.name}] [{level}] {message}{reset}", file=sys.stdout)

    def info(self, message):
        self._log('INFO', message)

    def warn(self, message):
        self._log('WARN', message)

    def error(self, message):
        self._log('ERROR', message)

    def debug(self, message):
        self._log('DEBUG', message)
