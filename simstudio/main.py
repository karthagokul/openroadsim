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
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QStatusBar
from menubar import SimStudioMenuBar, MenuAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimStudio — OpenRoadSim")
        self.resize(1200, 800)

        # Set status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Menu bar setup
        self.menu_bar = SimStudioMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.menu_triggered.connect(self.handle_menu_action)

        # Placeholder central widget
        self.label = QLabel("Welcome to SimStudio!", self)
        self.label.setStyleSheet("font-size: 18px; padding: 20px;")
        self.setCentralWidget(self.label)

    def handle_menu_action(self, action):
        self.status.showMessage(f"Menu action triggered: {action.name}", 3000)

        if action == MenuAction.OPEN_SCENARIO:
            self.label.setText("Opening scenario file...")
        elif action == MenuAction.RUN:
            self.label.setText("Starting simulation...")
        elif action == MenuAction.PAUSE:
            self.label.setText("Simulation paused.")
        elif action == MenuAction.ABOUT:
            self.label.setText("SimStudio v1.0 — Open source automotive simulator")
        else:
            self.label.setText(f"Triggered: {action.name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
