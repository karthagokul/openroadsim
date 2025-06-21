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
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def load_report(path):
    with open(path) as f:
        return json.load(f)

def visualize(report):
    responses = report["responses"]
    plugins = sorted(list({r["plugin"] for r in responses}))
    plugin_y = {p: i for i, p in enumerate(plugins)}

    fig, ax = plt.subplots(figsize=(16, max(4, len(plugins) * 0.8)))  # wider for scrolling

    x_vals = []

    for resp in responses:
        sim_time = float(resp.get("sim_time", 0.0))
        plugin = resp["plugin"]
        topic = resp["topic"]

        y = plugin_y[plugin]
        x = sim_time
        x_vals.append(x)

        ax.plot(x, y, 'o', label=plugin)
        ax.text(x, y + 0.15, topic, va="bottom", fontsize=7, alpha=0.7, rotation=45, ha="left")

    # Set plugin names on Y-axis
    ax.set_yticks(list(plugin_y.values()))
    ax.set_yticklabels(plugins)

    # X-axis = Simulation Time
    ax.set_xlabel("Simulation Time (s)")
    ax.set_title("📊 OpenRoadSim — Plugin Response Timeline")
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.set_ylim(-1, len(plugins))

    # Set wider x-limit based on data range
    if x_vals:
        ax.set_xlim(min(x_vals) - 1, max(x_vals) + 2)  # add margin for scrolling/panning

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    report = load_report("report.json")
    visualize(report)
