from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import pyqtSignal

class ClickableScene(QGraphicsScene):
    event_selected = pyqtSignal(dict)

    def mousePressEvent(self, event):
        pos = event.scenePos()  # Scene coordinates
        item = self.itemAt(pos, self.views()[0].transform())  # Correct usage
        if isinstance(item, QGraphicsRectItem):
            event_data = item.data(0)
            if isinstance(event_data, dict):
                print(f"[DEBUG] Clicked Event: {event_data}")  # Add this for debugging
                self.event_selected.emit(event_data)
        super().mousePressEvent(event)
