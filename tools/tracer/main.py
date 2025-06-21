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
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

class TracerApp(tk.Tk):
    def __init__(self, report_path=None):
        super().__init__()
        self.title("OpenRoadSim Tracer")
        self.geometry("900x600")

        self.report = None
        if report_path:
            self.load_report(report_path)
        else:
            self.report = {"responses": [], "events": []}

        self.plugins = []

        # Left frame: plugin list
        self.plugin_frame = ttk.Frame(self)
        self.plugin_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(self.plugin_frame, text="Plugins").pack(pady=5)
        self.plugin_listbox = tk.Listbox(self.plugin_frame, width=30)
        self.plugin_listbox.pack(expand=True, fill=tk.Y, padx=5)
        self.plugin_listbox.bind("<<ListboxSelect>>", self.on_plugin_select)

        # Right frame: event details
        self.detail_frame = ttk.Frame(self)
        self.detail_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        ttk.Label(self.detail_frame, text="Event Details").pack(pady=5)
        self.event_text = scrolledtext.ScrolledText(self.detail_frame, wrap=tk.WORD)
        self.event_text.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Populate plugin list
        if self.report:
            self.populate_plugins()

    def load_report(self, path):
        try:
            with open(path, "r") as f:
                self.report = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load report:\n{e}")
            self.report = {"responses": [], "events": []}

    def populate_plugins(self):
        self.plugins = sorted(set(r["plugin"] for r in self.report["responses"]))
        self.plugin_listbox.delete(0, tk.END)
        for p in self.plugins:
            self.plugin_listbox.insert(tk.END, p)

    def on_plugin_select(self, event):
        selection = self.plugin_listbox.curselection()
        if not selection:
            return
        plugin = self.plugin_listbox.get(selection[0])
        self.show_plugin_events(plugin)

    def show_plugin_events(self, plugin):
        events = [r for r in self.report["responses"] if r["plugin"] == plugin]
        self.event_text.delete(1.0, tk.END)
        for ev in events:
            topic = ev.get("topic", "(unknown)")
            sim_time = ev.get("sim_time", "(unknown)")
            real_time = ev.get("real_time", "(unknown)")
            response = ev.get("response", "(unknown)")
            # Find matching event data
            event_data = {}
            for e in self.report.get("events", []):
                if e.get("topic") == topic and abs(e.get("sim_time",0) - sim_time) < 0.001:
                    event_data = e.get("data", {})
                    break

            self.event_text.insert(tk.END, f"Topic: {topic}\n")
            self.event_text.insert(tk.END, f"Sim Time: {sim_time}\n")
            self.event_text.insert(tk.END, f"Real Time: {real_time}\n")
            self.event_text.insert(tk.END, f"Response: {response}\n")
            self.event_text.insert(tk.END, f"Data: {json.dumps(event_data, indent=2)}\n")
            self.event_text.insert(tk.END, "-"*50 + "\n\n")

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "report.json"
    app = TracerApp(path)
    app.mainloop()
