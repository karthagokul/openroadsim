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

from PyQt5.QtWidgets import QMainWindow, QMenuBar, QMenu, QAction
from PyQt5.QtCore import pyqtSignal, QObject
from enum import Enum, auto

class MenuAction(Enum):
    OPEN_SCENARIO = auto()
    SAVE_SCENARIO = auto()
    SAVE_AS = auto()
    RELOAD_SCENARIO = auto()
    EXIT = auto()
    RUN = auto()
    PAUSE = auto()
    RESUME = auto()
    STEP = auto()
    RESET = auto()
    LOAD_PLUGIN = auto()
    RELOAD_PLUGINS = auto()
    ENABLE_PLUGINS = auto()
    DISABLE_PLUGINS = auto()
    PLUGIN_MANAGER = auto()
    INJECT_EVENT = auto()
    SIGNAL_INSPECTOR = auto()
    TIMELINE_VIEW = auto()
    SCENARIO_EDITOR = auto()
    METRICS_VIEWER = auto()
    CAN_VIEWER = auto()
    DESCRIBE_SCENARIO = auto()
    GENERATE_TEST_CASE = auto()
    EDGE_CASE_SUGGESTIONS = auto()
    FIX_YAML_ERRORS = auto()
    CHAT_ASSISTANT = auto()
    CONNECT_CAN = auto()
    CONNECT_GPS = auto()
    SWITCH_MODE = auto()
    ECU_DASHBOARD = auto()
    TOGGLE_TIMELINE = auto()
    TOGGLE_PLUGIN = auto()
    TOGGLE_LOG = auto()
    TOGGLE_EDITOR = auto()
    RESET_LAYOUT = auto()
    USER_GUIDE = auto()
    SDK_DOCS = auto()
    SHORTCUT_KEYS = auto()
    REPORT_BUG = auto()
    CHECK_UPDATES = auto()
    ABOUT = auto()

class SimStudioMenuBar(QMenuBar):
    menu_triggered = pyqtSignal(MenuAction)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_menus()

    def _add_action(self, menu, text, action_enum):
        action = QAction(text, self)
        action.triggered.connect(lambda: self._emit_action(action_enum))
        menu.addAction(action)

    def _emit_action(self, action_enum):
        print(f"[Action] {action_enum.name}")
        self.menu_triggered.emit(action_enum)

    def _create_menus(self):
        self._create_file_menu()
        self._create_simulation_menu()
        self._create_plugins_menu()
        self._create_tools_menu()
        self._create_ai_menu()
        self._create_hardware_menu()
        self._create_view_menu()
        self._create_help_menu()

    def _create_file_menu(self):
        file_menu = self.addMenu("File")
        self._add_action(file_menu, "Open Scenario...", MenuAction.OPEN_SCENARIO)
        self._add_action(file_menu, "Save Scenario", MenuAction.SAVE_SCENARIO)
        self._add_action(file_menu, "Save As...", MenuAction.SAVE_AS)
        file_menu.addSeparator()
        self._add_action(file_menu, "Reload Scenario", MenuAction.RELOAD_SCENARIO)
        file_menu.addSeparator()
        self._add_action(file_menu, "Exit", MenuAction.EXIT)

    def _create_simulation_menu(self):
        sim_menu = self.addMenu("Simulation")
        self._add_action(sim_menu, "Run", MenuAction.RUN)
        self._add_action(sim_menu, "Pause", MenuAction.PAUSE)
        self._add_action(sim_menu, "Resume", MenuAction.RESUME)
        self._add_action(sim_menu, "Step Forward", MenuAction.STEP)
        sim_menu.addSeparator()
        self._add_action(sim_menu, "Stop / Reset", MenuAction.RESET)

    def _create_plugins_menu(self):
        plugins_menu = self.addMenu("Plugins")
        self._add_action(plugins_menu, "Load Plugin...", MenuAction.LOAD_PLUGIN)
        self._add_action(plugins_menu, "Reload Plugins", MenuAction.RELOAD_PLUGINS)
        self._add_action(plugins_menu, "Enable All Plugins", MenuAction.ENABLE_PLUGINS)
        self._add_action(plugins_menu, "Disable All Plugins", MenuAction.DISABLE_PLUGINS)
        self._add_action(plugins_menu, "Plugin Manager...", MenuAction.PLUGIN_MANAGER)

    def _create_tools_menu(self):
        tools_menu = self.addMenu("Tools")
        self._add_action(tools_menu, "Inject Event...", MenuAction.INJECT_EVENT)
        self._add_action(tools_menu, "Signal Inspector", MenuAction.SIGNAL_INSPECTOR)
        self._add_action(tools_menu, "Timeline View", MenuAction.TIMELINE_VIEW)
        self._add_action(tools_menu, "Scenario Editor", MenuAction.SCENARIO_EDITOR)
        self._add_action(tools_menu, "Metrics Viewer", MenuAction.METRICS_VIEWER)
        self._add_action(tools_menu, "CAN Viewer", MenuAction.CAN_VIEWER)

    def _create_ai_menu(self):
        ai_menu = self.addMenu("AI Assistant")
        self._add_action(ai_menu, "Describe Scenario", MenuAction.DESCRIBE_SCENARIO)
        self._add_action(ai_menu, "Generate Test Case", MenuAction.GENERATE_TEST_CASE)
        self._add_action(ai_menu, "Edge Case Suggestions", MenuAction.EDGE_CASE_SUGGESTIONS)
        self._add_action(ai_menu, "Fix YAML Errors", MenuAction.FIX_YAML_ERRORS)
        self._add_action(ai_menu, "Chat with Assistant", MenuAction.CHAT_ASSISTANT)

    def _create_hardware_menu(self):
        hw_menu = self.addMenu("Hardware")
        self._add_action(hw_menu, "Connect USB-CAN...", MenuAction.CONNECT_CAN)
        self._add_action(hw_menu, "Connect USB-GPS...", MenuAction.CONNECT_GPS)
        self._add_action(hw_menu, "Switch Mode", MenuAction.SWITCH_MODE)
        self._add_action(hw_menu, "Show ECU Dashboard", MenuAction.ECU_DASHBOARD)

    def _create_view_menu(self):
        view_menu = self.addMenu("View")
        self._add_action(view_menu, "Toggle Timeline Panel", MenuAction.TOGGLE_TIMELINE)
        self._add_action(view_menu, "Toggle Plugin Panel", MenuAction.TOGGLE_PLUGIN)
        self._add_action(view_menu, "Toggle Log Console", MenuAction.TOGGLE_LOG)
        self._add_action(view_menu, "Toggle Scenario Editor", MenuAction.TOGGLE_EDITOR)
        self._add_action(view_menu, "Reset Window Layout", MenuAction.RESET_LAYOUT)

    def _create_help_menu(self):
        help_menu = self.addMenu("Help")
        self._add_action(help_menu, "User Guide", MenuAction.USER_GUIDE)
        self._add_action(help_menu, "Plugin SDK Docs", MenuAction.SDK_DOCS)
        self._add_action(help_menu, "Shortcut Keys", MenuAction.SHORTCUT_KEYS)
        self._add_action(help_menu, "Report a Bug", MenuAction.REPORT_BUG)
        self._add_action(help_menu, "Check for Updates", MenuAction.CHECK_UPDATES)
        self._add_action(help_menu, "About SimStudio", MenuAction.ABOUT)