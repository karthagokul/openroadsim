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

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QCheckBox
from PyQt5.QtCore import QTimer
import can
import datetime

class CANViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CAN Viewer")
        self.resize(700, 400)

        self.interface_combo = QComboBox()
        self.interface_combo.addItems(["vcan0", "can0"])  # Extendable

        self.connect_button = QPushButton("Connect")
        self.clear_button = QPushButton("Clear")
        self.auto_scroll = QCheckBox("Auto Scroll")
        self.auto_scroll.setChecked(True)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Time", "CAN ID", "DLC", "Data", "Interface"])

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Interface:"))
        top_layout.addWidget(self.interface_combo)
        top_layout.addWidget(self.connect_button)
        top_layout.addWidget(self.clear_button)
        top_layout.addWidget(self.auto_scroll)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.connect_button.clicked.connect(self._start_capture)
        self.clear_button.clicked.connect(self.table.clearContents)
        self.clear_button.clicked.connect(lambda: self.table.setRowCount(0))

        self.timer = QTimer()
        self.timer.timeout.connect(self._read_messages)
        self.bus = None

    def _start_capture(self):
        iface = self.interface_combo.currentText()
        try:
            self.bus = can.interface.Bus(channel=iface, bustype='socketcan')
            self.timer.start(100)  # Check every 100 ms
            self.connect_button.setEnabled(False)
        except Exception as e:
            print(f"[CANViewer] Failed to connect to {iface}: {e}")

    def _read_messages(self):
        try:
            msg = self.bus.recv(timeout=0.01)
            if msg:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(datetime.datetime.now().strftime('%H:%M:%S')))
                self.table.setItem(row, 1, QTableWidgetItem(hex(msg.arbitration_id)))
                self.table.setItem(row, 2, QTableWidgetItem(str(msg.dlc)))
                self.table.setItem(row, 3, QTableWidgetItem(" ".join(f"{x:02X}" for x in msg.data)))
                self.table.setItem(row, 4, QTableWidgetItem(self.interface_combo.currentText()))

                if self.auto_scroll.isChecked():
                    self.table.scrollToBottom()
        except Exception as e:
            print(f"[CANViewer] Error reading CAN: {e}")
