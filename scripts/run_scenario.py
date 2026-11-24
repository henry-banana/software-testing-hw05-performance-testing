"""Run the EShop performance benchmark in an isolated local backend checkout."""

import argparse
import csv
import json
import re
import shutil
import socket
import subprocess
import time
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import psutil

from build_plans import DEFAULT_DATE, PLANS, ROOT, STUDENT_ID

PIN = "de0f48f5b40939692e7029943295d44788f617ea"
FIXTURE = ROOT / "data" / "workflow.csv"
LOCAL_HOST = "127.0.0.1"
MIN_AVAILABLE = 1200 * 1024 ** 2
BACKEND_LIMIT = 1400 * 1024 ** 2


def api(port, path, payload=None):
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(f"http://{LOCAL_HOST}:{port}{path}", body,
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=3) as response:
        return json.load(response)


def prepare_fixture(port):
    products = {p["id"]: p["price"] for p in api(port, "/api/products")}
    with FIXTURE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 384 or len({r["email"] for r in rows}) != len(rows):
        raise ValueError("Expected 384 distinct synthetic accounts")
    for index, row in enumerate(rows, 1):
        if not all(re.fullmatch(r"[A-Za-z0-9 .@-]+", value) for value in row.values()):
            raise ValueError(f"Use plain generated CSV values at fixture row {index}")
        if products.get(int(row["product_id"])) != int(row["total_amount"]):
            raise ValueError(f"Product ID or price mismatch at fixture row {index}")
        created = api(port, "/api/register",
                      {"name": f"HW05 VU {index:03d}", "email": row["email"],
                       "password": row["password"]})
        if not isinstance(created.get("id"), int):
            raise RuntimeError(f"Registration failed for fixture row {index}")
    return len(rows)


def wait_for_backend(backend, port):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and backend.poll() is None:
        try:
            products = api(port, "/api/products")
            if isinstance(products, list) and products:
                return
        except (URLError, TimeoutError, ValueError):
            pass
        time.sleep(0.25)
    raise RuntimeError("Backend did not seed and come up. Check backend.log.")


def command_output(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def require_isolated_checkout(path):
    if (path / "backend" / "server.js").is_file() and path != ROOT:
        branch = command_output("git", "rev-parse", "HEAD", cwd=path)
        if branch == PIN:
            code_status = command_output(
                "git", "status", "--porcelain", "--", "backend/server.js", "backend/database.js",
                cwd=path)
            if not code_status:
                return branch
    raise ValueError(f"--sut must point to a disposable EShop clone at {PIN} with unchanged backend code")


def stop(process):
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def record_resource(out, backend, jmeter, started):
    node = psutil.Process(backend.pid)
    java = psutil.Process(jmeter.pid)
    processes = [node, java]
    for process in processes:
        process.cpu_percent()
    psutil.cpu_percent()

    keys = ["timestamp", "elapsed_s", "backend_pid", "jmeter_pid", "backend_cpu_core_pct",
            "backend_rss_mib", "jmeter_cpu_core_pct", "jmeter_rss_mib", "system_cpu_pct",
            "available_mib"]
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(keys)
        while jmeter.poll() is None:
            time.sleep(1)
            if backend.poll() is not None:
                raise RuntimeError("Backend exited during the run. Check backend.log.")
            try:
                node_rss = node.memory_info().rss
                java_rss = java.memory_info().rss
            except psutil.NoSuchProcess:
                if jmeter.poll() is not None:
                    break
                raise
            available = psutil.virtual_memory().available
            writer.writerow([datetime.now().astimezone().isoformat(timespec="milliseconds"),
                             round(time.monotonic() - started, 2), node.pid, java.pid,
                             node.cpu_percent(), round(node_rss / 1024 ** 2, 2),
                             java.cpu_percent(), round(java_rss / 1024 ** 2, 2),
                             psutil.cpu_percent(), round(available / 1024 ** 2, 2)])
            handle.flush()
            if available < MIN_AVAILABLE or node_rss > BACKEND_LIMIT:
                raise RuntimeError("Memory limit reached. Raw run files retained; measurement halted.")


def run(args):
    sut = args.sut.resolve()
    jmeter_home = args.jmeter.resolve()
    jar = jmeter_home / "bin" / "ApacheJMeter.jar"
    if not jar.is_file():
        raise ValueError("--jmeter must point to the Apache JMeter installation folder")
    pin = require_isolated_checkout(sut)
    with socket.socket() as probe:
        probe.settimeout(0.5)
        if probe.connect_ex((LOCAL_HOST, 3000)) == 0:
            raise RuntimeError("Port 3000 already in use. Stop only the intended test backend first.")
    java = str(args.java.resolve()) if args.java else shutil.which("java")
    node = shutil.which("node")
    if not java or not node:
        raise RuntimeError("Java and Node.js must be on PATH")
    source_plan = "Load" if args.mode in ("smoke", "endurance") else args.scenario
    name = f"{STUDENT_ID}_{source_plan}_{args.date}"
    plan = ROOT / "test-plans" / f"{name}.jmx"
    if not plan.is_file():
        raise FileNotFoundError(plan)
    label = args.scenario.lower() if args.mode == "measure" else args.mode
    if not re.fullmatch(r"[a-z0-9-]+", args.run_id):
        raise ValueError("Use lowercase letters, digits and hyphens in --run-id")
    out = ROOT / "results" / label / args.run_id
    out.mkdir(parents=True, exist_ok=False)
    overrides = []
    if args.mode != "measure":
        count, ramp, duration = (2, 1, 10) if args.mode == "smoke" else (
            args.vus, min(20, args.vus), 20 + args.seconds)
        overrides = [f"-Jnum_threads_1={count}", f"-Jramp_time_1={ramp}", f"-Jduration_1={duration}"]
    jtl = out / f"{label}.jtl"
    conf = [
        f"-Jfixture={FIXTURE}", "-Jjmeter.save.saveservice.output_format=csv",
        "-Jjmeter.save.saveservice.print_field_names=true",
        "-Jjmeter.save.saveservice.assertion_results_failure_message=true",
        "-Jjmeter.save.saveservice.timestamp_format=ms",
        "-Jhttpclient4.retrycount=0",
    ]
    if args.mode != "measure" and args.mode == "smoke":
        conf += ["-Jthink_min=50", "-Jthink_range=10"]
    command = [java, "-Xms128m", "-Xmx768m", "-Xss512k", "-jar", str(jar),
               "-n", "-t", str(plan), "-l", str(jtl), "-j", str(out / "jmeter.log"),
               "-e", "-o", str(out / "html"), *conf, *overrides]
    open_hidden = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    backend = jmeter = None
    metadata = {
        "scenario": label, "run_id": args.run_id, "sut_commit": pin,
        "plan": plan.name, "node": command_output(node, "--version"),
        "java": command_output(java, "--version").splitlines()[0],
        "jmeter": "5.6.3",
        "fixture_rows": 0, "hostname": socket.gethostname(), "operator": "Codex CLI",
        "behavior": "Disposable local EShop seeded anew by startup",
        "overrides": overrides, "status": "failed",
    }
    try:
        with (out / "backend.log").open("wb") as backend_log, (out / "console.log").open("wb") as jmeter_log:
            backend = subprocess.Popen([node, "server.js"], cwd=sut / "backend",
                                       stdout=backend_log, stderr=subprocess.STDOUT,
                                       creationflags=open_hidden)
            wait_for_backend(backend, 3000)
            metadata["fixture_rows"] = prepare_fixture(3000)
            metadata["started_at"] = datetime.now().astimezone().isoformat(timespec="milliseconds")
            started = time.monotonic()
            print(f"{label}: fixture ready, starting measured CLI. Output {out}", flush=True)
            jmeter = subprocess.Popen(command, cwd=ROOT, stdout=jmeter_log,
                                      stderr=subprocess.STDOUT, creationflags=open_hidden)
            record_resource(out / "resources.csv", backend, jmeter, started)
            if jmeter.wait() != 0 or not jtl.is_file() or not (out / "html" / "index.html").is_file():
                raise RuntimeError("JMeter CLI or dashboard failed. Check console.log and jmeter.log.")
            console = (out / "console.log").read_text(encoding="utf-8", errors="replace")
            start = re.search(r"Starting standalone test @ .+ \((\d+)\)", console)
            if not start or "Uncaught Exception" in console:
                raise RuntimeError("JMeter did not complete normally. Check console.log.")
            metadata["jmeter_start_ms"] = int(start.group(1))
            metadata["status"] = "completed"
    finally:
        stop(jmeter)
        stop(backend)
        metadata["finished_at"] = datetime.now().astimezone().isoformat(timespec="milliseconds")
        (out / "run.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"{label}: JTL and HTML dashboard saved to {out}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sut", type=Path, required=True, help="disposable clone; startup resets SQLite")
    parser.add_argument("--jmeter", type=Path, required=True)
    parser.add_argument("--java", type=Path, help="java executable, such as the installed JDK 21")
    parser.add_argument("--scenario", choices=PLANS, default="Load")
    parser.add_argument("--mode", choices=("smoke", "measure", "endurance"), default="measure")
    parser.add_argument("--date", default=DEFAULT_DATE)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--vus", type=int, default=48)
    parser.add_argument("--seconds", type=int, default=720, help="endurance plateau duration")
    args = parser.parse_args()
    if not 1 <= args.vus <= 384 or not 600 <= args.seconds <= 900:
        parser.error("Endurance supports 1 to 384 VUs and a plateau of 600 to 900 seconds")
    run(args)


if __name__ == "__main__":
    main()
