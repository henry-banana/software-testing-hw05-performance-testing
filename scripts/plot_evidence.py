"""Draw charts from recorded resource samples and original JMeter JTL files."""

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

ROOT = Path(__file__).resolve().parents[1]
INK = "#213447"
TEAL = "#14746f"
BLUE = "#285f99"
MUTED = "#66788a"
GRID = "#e3eaf0"


def plot_run(run):
    metadata = json.loads((run / "run.json").read_text(encoding="utf-8"))
    metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    start_ms = metadata["jmeter_start_ms"]
    mode = metadata["scenario"]
    with (run / f"{mode}.jtl").open(encoding="utf-8", newline="") as source:
        buckets = Counter(
            (int(row["timeStamp"]) + int(row["elapsed"]) - start_ms) // 5000
            for row in csv.DictReader(source))
    with (run / "resources.csv").open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    elapsed = [(datetime.fromisoformat(row["timestamp"]).timestamp() * 1000 - start_ms) / 1000
               for row in rows]
    start, end = max(0, min(buckets)), max(buckets)

    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(9.8, 6.8))
    fig.subplots_adjust(left=.12, right=.96, top=.85, bottom=.10, hspace=.22)
    fig.text(.12, .94, f"{mode.title()} | {metadata['run_id']}", fontsize=20,
             fontweight="bold", color=INK)
    fig.text(.12, .895, "JMeter HTTP samples and measured process resources", fontsize=10, color=MUTED)
    axes[0].step([i * 5 for i in range(start, end + 2)],
                 [buckets[i] / 5 for i in range(start, end + 1)] + [buckets[end] / 5],
                 where="post", color=TEAL)
    axes[0].set_ylabel("Requests/s")
    axes[1].plot(elapsed, [float(r["backend_cpu_core_pct"]) for r in rows], label="Node", color=TEAL)
    axes[1].plot(elapsed, [float(r["jmeter_cpu_core_pct"]) for r in rows], label="JMeter", color=BLUE)
    axes[1].set_ylabel("CPU (% of one core)")
    axes[2].plot(elapsed, [float(r["backend_rss_mib"]) for r in rows], label="Node", color=TEAL)
    axes[2].plot(elapsed, [float(r["jmeter_rss_mib"]) for r in rows], label="JMeter", color=BLUE)
    axes[2].set_ylabel("Working set (MiB)")
    axes[2].set_xlabel("Seconds from JMeter start")
    for ax in axes:
        ax.set_xlim(0, max(end * 5 + 5, max(elapsed)))
        ax.grid(axis="y", color=GRID)
        ax.spines[["top", "right"]].set_visible(False)
        for window in metrics["windows"]:
            if mode == "endurance" and window["window"] != "plateau":
                continue
            ax.axvspan(window["from_s"], window["to_s"], color=TEAL, alpha=.055)
    axes[1].legend(loc="upper left", frameon=False, ncols=2)
    fig.savefig(ROOT / "evidence" / f"{mode}-metrics.png", dpi=140, facecolor="white")
    plt.close(fig)


def flow():
    fig, ax = plt.subplots(figsize=(9.8, 5.2))
    ax.set(xlim=(0, 12), ylim=(0, 7))
    ax.axis("off")
    ax.text(.3, 6.65, "Continuous performance testing", fontsize=20, fontweight="bold", color=INK)

    def box(x, y, label, diamond=False):
        if diamond:
            patch = Polygon([(x-1.37, y), (x, y+.54), (x+1.37, y), (x, y-.54)],
                            fc="#edf7f6", ec=TEAL, linewidth=1.2)
        else:
            patch = FancyBboxPatch((x-1.34, y-.3), 2.68, .60,
                                   boxstyle="round,pad=.08", fc="#f3f7fb", ec=BLUE, linewidth=1.1)
        ax.add_patch(patch)
        ax.text(x, y, label, ha="center", va="center", color=INK, fontsize=9)

    def arrow(a, b, label=None):
        ax.annotate("", xy=b, xytext=a,
                    arrowprops={"arrowstyle": "-|>", "color": MUTED, "lw": 1.0})
        if label:
            ax.text((a[0]+b[0])/2 + .13, (a[1]+b[1])/2 + .12, label,
                    color=MUTED, fontsize=8)

    box(5.8, 5.95, "Commit or scheduled run")
    box(5.8, 4.90, "Run test?", True)
    box(9.6, 4.90, "Skip and record reason")
    box(5.8, 3.70, "Run base and candidate")
    box(5.8, 2.60, "p95 over limit?", True)
    box(2.0, 2.60, "Pass and retain reports")
    box(5.8, 1.45, "Repeat matched pairs")
    box(5.8, .45, "Confirmed in 2 of 3?", True)
    box(2.0, .45, "Review noise and evidence")
    box(9.6, .45, "Flag p95 regression")
    arrow((5.8, 5.56), (5.8, 5.47))
    arrow((7.18, 4.90), (8.18, 4.90), "No")
    arrow((5.8, 4.35), (5.8, 4.10), "Yes")
    arrow((5.8, 3.28), (5.8, 3.16))
    arrow((4.42, 2.60), (3.42, 2.60), "No")
    arrow((5.8, 2.05), (5.8, 1.85), "Yes")
    arrow((5.8, 1.06), (5.8, 1.00))
    arrow((4.42, .45), (3.42, .45), "No")
    arrow((7.18, .45), (8.18, .45), "Yes")
    fig.savefig(ROOT / "evidence" / "continuous-performance-testing.png",
                dpi=160, bbox_inches="tight", pad_inches=.18, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="*", type=Path)
    parser.add_argument("--flow", action="store_true")
    args = parser.parse_args()
    if args.flow:
        flow()
    for run_dir in args.runs:
        plot_run(run_dir)
