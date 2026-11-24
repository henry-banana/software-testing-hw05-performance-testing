"""Check the known EShop lockout behavior outside the measured workloads."""

import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError

from run_scenario import ROOT, api, require_free_port, require_isolated_checkout, stop, wait_for_backend

ACCOUNT = {"email": "lockout-check@hw05.example.test", "password": "Hw05DiagnosticOnly"}


def login(payload):
    try:
        data = api(3000, "/api/login", payload)
        return {"http": 200, "token_present": bool(data.get("token"))}
    except HTTPError as exc:
        data = json.load(exc)
        return {"http": exc.code, "error": data.get("error")}


def check(sut, locked_test, log):
    require_free_port(3000)
    hidden = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    backend = subprocess.Popen(["node", "server.js"], cwd=sut / "backend",
                               stdout=log, stderr=subprocess.STDOUT, creationflags=hidden)
    try:
        wait_for_backend(backend, 3000)
        api(3000, "/api/register", {"name": "HW05 lockout check", **ACCOUNT})
        if not locked_test:
            return [login(ACCOUNT)]
        invalid = {**ACCOUNT, "password": "WrongSyntheticPassword"}
        first = login(invalid)
        time.sleep(0.25)
        second = login(invalid)
        time.sleep(0.25)
        return [first, second, login(ACCOUNT)]
    finally:
        stop(backend)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sut", type=Path, required=True)
    args = parser.parse_args()
    pin = require_isolated_checkout(args.sut.resolve())
    out = ROOT / "evidence" / "lockout-check"
    out.mkdir(exist_ok=False)
    with (out / "backend.log").open("wb") as log:
        results = {"sut": pin, "at": datetime.now().astimezone().isoformat(),
                   "sequential_attempts": check(args.sut, True, log),
                   "valid_login_after_restart_and_reseed": check(args.sut, False, log)}
    (out / "responses.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=True))


if __name__ == "__main__":
    main()
