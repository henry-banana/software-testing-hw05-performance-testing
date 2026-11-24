"""Independently check JMeter CSV JTL samples and summarize measured windows."""

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import fmean, pstdev

from build_plans import LABELS, ROOT

WINDOWS = {
    "load": [("steady", 20, 95)],
    "stress": [(f"{vus} VU", i * 40 + 10, i * 40 + 38)
               for i, vus in enumerate((16, 48, 96, 192, 384))],
    "spike": [("base", 12, 28), ("spike", 35, 54), ("recovery", 62, 95)],
}


def percentile(values, p):
    if not values:
        return None
    return sorted(values)[max(0, math.ceil(len(values) * p / 100) - 1)]


def timely_sample(raw):
    if raw["label"] not in LABELS or raw["success"] not in ("true", "false"):
        raise ValueError(f"Unexpected sample type: {raw['label']}")
    return {"start": int(raw["timeStamp"]), "elapsed": int(raw["elapsed"]),
            "label": raw["label"], "success": raw["success"] == "true",
            "code": raw["responseCode"], "bytes": int(raw["bytes"]),
            "sent": int(raw["sentBytes"]), "latency": int(raw["Latency"]),
            "thread": raw["threadName"], "active": int(raw["allThreads"]),
            "failure": raw["failureMessage"]}


def end_ms(sample):
    return sample["start"] + sample["elapsed"]


def compute(samples, seconds):
    if not samples:
        return {"samples": 0, "rps": 0, "error_pct": None, "p95_ms": None}
    times = [s["elapsed"] for s in samples]
    failed = [s for s in samples if not s["success"]]
    history = [s["bytes"] for s in samples if s["label"] == LABELS[-1] and s["success"]]
    return {
        "samples": len(samples), "seconds": round(seconds, 3),
        "errors": len(failed), "error_pct": round(100 * len(failed) / len(samples), 4),
        "failure_codes": dict(Counter(s["code"] for s in failed)),
        "failures": dict(Counter(s["failure"] or s["code"] for s in failed)),
        "rps": round(len(samples) / seconds, 3),
        "history_success_per_s": round(len(history) / seconds, 3),
        "history_mean_bytes": round(fmean(history), 1) if history else None,
        "histories": len(history), "peak_active_vu": max(s["active"] for s in samples),
        "min_ms": min(times), "max_ms": max(times), "avg_ms": round(fmean(times), 2),
        "stddev_ms": round(pstdev(times), 2),
        "p50_ms": percentile(times, 50), "p90_ms": percentile(times, 90),
        "p95_ms": percentile(times, 95), "p99_ms": percentile(times, 99),
        "rx_kib_s": round(sum(s["bytes"] for s in samples) / seconds / 1024, 2),
        "tx_kib_s": round(sum(s["sent"] for s in samples) / seconds / 1024, 2),
        "avg_bytes": round(fmean(s["bytes"] for s in samples), 1),
    }


def resource_summary(resources, left=None, right=None):
    rows = []
    for row in resources:
        timestamp = datetime.fromisoformat(row["timestamp"]).timestamp() * 1000
        if (left is None or left <= timestamp) and (right is None or timestamp < right):
            rows.append(row)
    metrics = ("backend_cpu_core_pct", "backend_rss_mib", "jmeter_cpu_core_pct",
               "jmeter_rss_mib", "system_cpu_pct")
    return {"samples": len(rows),
            **{f"max_{col}": max(float(r[col]) for r in rows) for col in metrics},
            **{f"median_{col}": percentile([float(r[col]) for r in rows], 50) for col in metrics},
            "first_backend_rss_mib": float(rows[0]["backend_rss_mib"]),
            "last_backend_rss_mib": float(rows[-1]["backend_rss_mib"]),
            "min_available_mib": min(float(r["available_mib"]) for r in rows)} if rows else {
                "samples": 0}


def measure_window(samples, resources, start_ms, name, start, stop):
    left, right = start_ms + start * 1000, start_ms + stop * 1000
    window = [sample for sample in samples if left <= end_ms(sample) < right]
    width = stop - start
    result = compute(window, width)
    by_label = {label: compute([s for s in window if s["label"] == label], width)
                for label in LABELS}
    buckets = Counter((end_ms(sample) - left) // 10000 for sample in window)
    ten_seconds = [round(buckets[i] / 10, 1) for i in range(int(width // 10))]
    within = bool(window) and result["error_pct"] <= 1 and all(
        metric["p95_ms"] is not None and metric["p95_ms"] <= 250
        for metric in by_label.values())
    return {"window": name, "from_s": start, "to_s": stop, **result,
            "within_p95_and_errors": within, "full_10s_rps": ten_seconds,
            "per_label_p95_ms": {key: val["p95_ms"] for key, val in by_label.items()},
            "resources": resource_summary(resources, left, right)}


def write_table(path, rows, columns):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["label", *columns])
        writer.writerows([label, *(metrics[k] for k in columns)] for label, metrics in rows.items())


def write_views(directory, mode, table, samples, start_ms):
    if mode == "load":
        write_table(directory / "summary-report.csv", table,
                    ["samples", "avg_ms", "min_ms", "max_ms", "stddev_ms",
                     "error_pct", "rps", "rx_kib_s", "tx_kib_s", "avg_bytes"])
    elif mode == "stress":
        write_table(directory / "aggregate-report.csv", table,
                    ["samples", "avg_ms", "p50_ms", "p90_ms", "p95_ms", "p99_ms",
                     "min_ms", "max_ms", "error_pct", "rps"])
    elif mode == "spike":
        records = {}
        for name, index, _ in WINDOWS["spike"]:
            at = start_ms + index * 1000
            chosen = {}
            for sample in samples:
                if end_ms(sample) >= at and sample["label"] not in chosen:
                    chosen[sample["label"]] = sample
                if len(chosen) == len(LABELS):
                    break
            records[name] = chosen
        (directory / "sample-details.json").write_text(
            json.dumps(records, indent=2) + "\n", encoding="utf-8")


def analyze(directory):
    info = json.loads((directory / "run.json").read_text(encoding="utf-8"))
    if info["status"] != "completed":
        raise ValueError(f"Cannot analyze incomplete run {directory}")
    mode, start = info["scenario"], info["jmeter_start_ms"]
    jtl = directory / f"{mode}.jtl"
    with jtl.open(encoding="utf-8", newline="") as handle:
        samples = [timely_sample(row) for row in csv.DictReader(handle)]
    if not samples:
        raise ValueError(f"No samples in {jtl}")
    with (directory / "resources.csv").open(encoding="utf-8", newline="") as handle:
        resource = list(csv.DictReader(handle))
    duration = (max(map(end_ms, samples)) - min(s["start"] for s in samples)) / 1000
    stats = {"Total": compute(samples, duration)}
    stats.update((label, compute([s for s in samples if s["label"] == label], duration))
                 for label in LABELS)
    dashboard = json.loads((directory / "html" / "statistics.json").read_text(encoding="utf-8"))
    for name, numbers in stats.items():
        if numbers["samples"] != dashboard[name]["sampleCount"]:
            raise ValueError(f"JTL and HTML sample counts differ for {name}")
        if numbers["errors"] != dashboard[name]["errorCount"]:
            raise ValueError(f"JTL and HTML failure counts differ for {name}")

    intervals = WINDOWS.get(mode, [])
    if mode == "endurance":
        plateau_seconds = int(next(v.rsplit("=", 1)[1] for v in info["overrides"]
                                   if v.startswith("-Jduration_1="))) - 20
        end = 20 + plateau_seconds
        intervals = [("plateau", 20, end), ("first minute", 20, 80),
                     ("last minute", end - 60, end)]
        intervals += [(f"minute {minute + 1:02d}", start_s, min(end, start_s + 60))
                      for minute, start_s in enumerate(range(20, end, 60))]
    result = {"run_id": info["run_id"], "scenario": mode, "jmeter_start_ms": start,
              "first_jtl_ms": min(s["start"] for s in samples),
              "last_jtl_completion_ms": max(map(end_ms, samples)),
              "stats": stats,
              "dashboard_total": dashboard["Total"],
              "resources": resource_summary(resource),
              "windows": [measure_window(samples, resource, start, *interval) for interval in intervals]}
    (directory / "metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    write_views(directory, mode, stats, sorted(samples, key=end_ms), start)
    print(f"{mode}: {len(samples)} samples, {stats['Total']['errors']} failed, "
          f"{stats['Total']['rps']:.2f} RPS, p95 {stats['Total']['p95_ms']} ms")
    for window in result["windows"]:
        print(f"  {window['window']}: {window['rps']:.2f} RPS, {window['error_pct']}% error, "
              f"p95 {window['p95_ms']} ms, endpoint p95 {window['per_label_p95_ms']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", type=Path, nargs="+")
    for directory in parser.parse_args().directories:
        analyze(directory if directory.is_absolute() else ROOT / directory)
