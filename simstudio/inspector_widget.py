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
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit,
    QFileDialog, QMessageBox, QSplitter, QPushButton, QLabel
)
from PyQt5.QtCore import Qt

class InspectorWidget(QWidget):
    def __init__(self, report_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inspector")
        self.report = {"responses": [], "events": []}
        self.report_path = report_path

        self._setup_ui()

        # Load file if provided
        if self.report_path:
            self.load_report(self.report_path)
            self.populate_plugins()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 🔍 File selector bar
        top_bar = QHBoxLayout()
        self.path_label = QLabel("No file loaded")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_report)
        top_bar.addWidget(self.path_label)
        top_bar.addStretch()
        top_bar.addWidget(browse_btn)
        layout.addLayout(top_bar)

        # 🧱 Main content area (split)
        splitter = QSplitter(Qt.Horizontal)

        self.plugin_list = QListWidget()
        self.plugin_list.currentItemChanged.connect(self.on_plugin_selected)
        splitter.addWidget(self.plugin_list)

        self.event_viewer = QTextEdit()
        self.event_viewer.setReadOnly(True)
        splitter.addWidget(self.event_viewer)
        splitter.setSizes([200, 700])

        layout.addWidget(splitter)

    def browse_report(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Simulation Report", "", "JSON Files (*.json);;All Files (*)"
        )
        if path:
            self.report_path = path
            self.path_label.setText(path)
            self.load_report(path)
            self.populate_plugins()

    def load_report(self, path):
        try:
            with open(path, 'r') as f:
                self.report = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load report:\n{e}")
            self.report = {"responses": [], "events": []}
            self.plugin_list.clear()
            self.event_viewer.clear()

    def populate_plugins(self):
        plugins = sorted(set(r["plugin"] for r in self.report.get("responses", [])))
        self.plugin_list.clear()
        self.plugin_list.addItems(plugins)

    def on_plugin_selected(self):
        current_item = self.plugin_list.currentItem()
        if not current_item:
            return
        plugin = current_item.text()
        self.show_plugin_events(plugin)

    def show_plugin_events(self, plugin):
        responses = [r for r in self.report["responses"] if r.get("plugin") == plugin]
        self.event_viewer.clear()

        for r in responses:
            topic = r.get("topic", "(unknown)")
            sim_time = r.get("sim_time", "(unknown)")
            real_time = r.get("real_time", "(unknown)")
            response = r.get("response", "(unknown)")

            matching_event = next(
                (e for e in self.report.get("events", [])
                 if e.get("topic") == topic and abs(e.get("sim_time", 0) - sim_time) < 0.001),
                {}
            )
            data = matching_event.get("data", {})

            self.event_viewer.append(f"Topic: {topic}")
            self.event_viewer.append(f"Sim Time: {sim_time}")
            self.event_viewer.append(f"Real Time: {real_time}")
            self.event_viewer.append(f"Response: {response}")
            self.event_viewer.append(f"Data:\n{json.dumps(data, indent=2)}")
            self.event_viewer.append("-" * 50 + "\n")
