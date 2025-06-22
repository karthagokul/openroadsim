from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QTextEdit, QSizePolicy
)
import json

class ScenarioPropertyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Event Properties")

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.target_label = QLabel("")
        self.time_label = QLabel("")
        self.action_label = QLabel("")
        self.params_text = QTextEdit()
        self.params_text.setReadOnly(True)
        self.params_text.setMinimumHeight(100)
        self.params_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.form_layout.addRow("Target:", self.target_label)
        self.form_layout.addRow("Time:", self.time_label)
        self.form_layout.addRow("Action:", self.action_label)
        self.form_layout.addRow("Params:", self.params_text)

        self.layout.addLayout(self.form_layout)

    def load_event(self, event):
        self.target_label.setText(str(event.get("target", "")))
        self.time_label.setText(str(event.get("time", "")))
        self.action_label.setText(str(event.get("action", "")))

        params = event.get("params", {})
        pretty = json.dumps(params, indent=2) if isinstance(params, dict) else str(params)
        self.params_text.setPlainText(pretty)

    def clear(self):
        self.target_label.setText("")
        self.time_label.setText("")
        self.action_label.setText("")
        self.params_text.clear()
