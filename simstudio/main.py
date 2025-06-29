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

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QMdiArea, QMdiSubWindow,QDockWidget
from PyQt5.QtCore import Qt
from menubar import SimStudioMenuBar, MenuAction
from can_viewer import CANViewerWidget
from inspector_widget import InspectorWidget
from scenario_timeline import ScenarioTimelineWidget
from log_console_widget import LogConsoleWidget
from PyQt5.QtWidgets import QFileDialog, QMdiSubWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimStudio — OpenRoadSim")
        self.resize(1200, 800)

        # Set up the MDI area
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)

        # Optional: Tabbed view for subwindows
        self.mdi_area.setViewMode(QMdiArea.TabbedView)
        self.mdi_area.setTabsClosable(True)
        self.mdi_area.setTabsMovable(True)

        # Set up the menu bar
        self.menu_bar = SimStudioMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.menu_triggered.connect(self.handle_menu_action)

        # Log Console setup
        self.log_console = LogConsoleWidget()
        dock = QDockWidget("Logs", self)
        dock.setWidget(self.log_console)
        dock.setObjectName("LogDock")
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def handle_menu_action(self, action):
        if action == MenuAction.CAN_VIEWER:
            self.open_can_viewer()
        elif action == MenuAction.SIGNAL_INSPECTOR:
            self.open_inspector()
        elif action == MenuAction.OPEN_SCENARIO:
            self.open_scenario()
        elif action == MenuAction.TOGGLE_LOG:
            self.show_log_console()
        else:
            print("to be implemented")

    def show_log_console(self):
        existing_dock = self.findChild(QDockWidget, "LogDock")
        if existing_dock:
            existing_dock.show()
            existing_dock.raise_()
            return

        self.log_console = LogConsoleWidget()
        dock = QDockWidget("Logs", self)
        dock.setWidget(self.log_console)
        dock.setObjectName("LogDock")
        dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)


    def open_can_viewer(self):
        can_widget = CANViewerWidget()
        subwindow = QMdiSubWindow()
        subwindow.setWidget(can_widget)
        subwindow.setAttribute(Qt.WA_DeleteOnClose)
        subwindow.setWindowTitle("CAN Viewer")
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def open_inspector(self):
        inspector = InspectorWidget()  # path can be parameterized
        subwindow = QMdiSubWindow()
        subwindow.setWidget(inspector)
        subwindow.setAttribute(Qt.WA_DeleteOnClose)
        subwindow.setWindowTitle("Signal Inspector")
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()
    
    def open_scenario(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Scenario YAML", "", "YAML Files (*.yaml *.yml)")
        if path:
            timeline = ScenarioTimelineWidget(path)
            sub = QMdiSubWindow()
            sub.setWidget(timeline)
            sub.setWindowTitle(f"Scenario: {path.split('/')[-1]}")
            sub.setAttribute(Qt.WA_DeleteOnClose)
            self.mdi_area.addSubWindow(sub)
            sub.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
