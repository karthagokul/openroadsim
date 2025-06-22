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

import yaml
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsSimpleTextItem, QFileDialog,
    QPushButton, QLabel, QHBoxLayout,QSplitter
)
from PyQt5.QtGui import QPen, QBrush, QPainter
from PyQt5.QtCore import Qt, QRectF
from scenario_property import ScenarioPropertyWidget
from clickable_scene import ClickableScene
from PyQt5.QtWidgets import QPlainTextEdit

class ScenarioTimelineWidget(QWidget):
    def __init__(self, yaml_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scenario Timeline")

        # Top bar: File path and Browse button
        file_bar = QHBoxLayout()
        self.path_label = QLabel("No scenario loaded")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_scenario)
        file_bar.addWidget(self.path_label)
        file_bar.addStretch()
        file_bar.addWidget(browse_btn)

        # Timeline View | Property Panel
        self.property_panel = ScenarioPropertyWidget()
        self.scene = ClickableScene()
        self.scene.event_selected.connect(self.property_panel.load_event)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints() | QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        timeline_splitter = QSplitter(Qt.Horizontal)
        timeline_splitter.addWidget(self.view)
        timeline_splitter.addWidget(self.property_panel)
        timeline_splitter.setSizes([int(self.width() * 0.8), int(self.width() * 0.2)])

        # YAML Editor
        self.yaml_editor = QPlainTextEdit()
        self.yaml_editor.setPlaceholderText("YAML scenario (editable)")
        self.yaml_editor.setStyleSheet("font-family: monospace;")
        self.yaml_editor.setLineWrapMode(QPlainTextEdit.NoWrap)

        # Final Vertical Splitter (Top: Timeline, Bottom: YAML)
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(timeline_splitter)
        main_splitter.addWidget(self.yaml_editor)
        main_splitter.setSizes([int(self.height() * 0.5), int(self.height() * 0.5)])

        # Master layout
        layout = QVBoxLayout(self)
        layout.addLayout(file_bar)
        layout.addWidget(main_splitter)

        if yaml_path:
            self.load_and_render(yaml_path)


    def browse_scenario(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Scenario File", "", "YAML Files (*.yaml *.yml)")
        if path:
            self.load_and_render(path)

    def load_and_render(self, path):
        with open(path, 'r') as f:
            text = f.read()
            data = yaml.safe_load(text)
            self.yaml_editor.setPlainText(text) 
        self.path_label.setText(path)
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)

                # Flexible: support top-level list or {"events": [...]}
                if isinstance(data, list):
                    events = data
                elif isinstance(data, dict) and "events" in data:
                    events = data["events"]
                else:
                    events = []

                self.render_timeline(events)
        except Exception as e:
            self.path_label.setText(f"Error loading: {e}")


    def render_timeline(self, events):
        self.scene.clear()
        LEFT = 100
        ROW_HEIGHT = 40
        EVENT_SIZE = 20
        TIME_SCALE = 100  # px per sec

        # Normalize keys: map 'target' → 'topic', 'time' → 'sim_time'
        valid_events = []
        for e in events:
            if isinstance(e, dict) and "time" in e and "target" in e:
                try:
                    sim_time = float(e["time"])
                    topic = str(e["target"])
                    e_copy = dict(e)  # make a shallow copy
                    e_copy["sim_time"] = sim_time
                    e_copy["topic"] = topic
                    valid_events.append({"sim_time": sim_time, "topic": topic, "full_event": e_copy})
                except (ValueError, TypeError):
                    continue  # skip invalid rows

        topics = sorted(set(e["topic"] for e in valid_events))
        topic_y = {t: i * ROW_HEIGHT for i, t in enumerate(topics)}
        max_time = max((e["sim_time"] for e in valid_events), default=10)

        for topic, y in topic_y.items():
            self.scene.addLine(LEFT, y + ROW_HEIGHT//2, LEFT + max_time*TIME_SCALE, y + ROW_HEIGHT//2, QPen(Qt.gray))
            label = QGraphicsSimpleTextItem(topic)
            label.setPos(10, y + 5)
            self.scene.addItem(label)

        for sec in range(int(max_time) + 1):
            x = LEFT + sec * TIME_SCALE
            self.scene.addLine(x, 0, x, len(topics)*ROW_HEIGHT, QPen(Qt.lightGray, 1, Qt.DashLine))
            label = QGraphicsSimpleTextItem(f"{sec}s")
            label.setPos(x - 10, len(topics)*ROW_HEIGHT + 5)
            self.scene.addItem(label)

        for e in valid_events:
            x = LEFT + e["sim_time"] * TIME_SCALE
            y = topic_y[e["topic"]] + ROW_HEIGHT//2 - EVENT_SIZE//2
            marker = QGraphicsRectItem(QRectF(x, y, EVENT_SIZE, EVENT_SIZE))
            marker.setBrush(QBrush(Qt.black))
            marker.setToolTip(f"{e['topic']}\nTime: {e['sim_time']}")
            marker.setData(0, e["full_event"])
            self.scene.addItem(marker)

        self.scene.setSceneRect(0, 0, LEFT + max_time * TIME_SCALE + 200, len(topics) * ROW_HEIGHT + 80)
    