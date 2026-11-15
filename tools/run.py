#!/usr/bin/env python3
"""The full pinned run (step 7, issue #8): one entry point behind `just all`.

    uv run python -m tools.run [--date YYYY-MM-DD] [--skip-speed] [--allow-dirty]

Steps, each stopping the run on failure: fetch the external sources (SHA-256 checked); convert every set to
`build/sets/`; run every adapter on every set and refuse the run if the libpostal build is not the pinned one; copy the
prediction files to `runs/DATE/predictions/` (committed, so anyone can rescore); score them into `runs/DATE/results.md`
and `results.json`; measure speed and size into `runs/DATE/speed.md` and `speed.json`; write `runs/DATE/run.json` (the
commit, parser versions, each set's SHA-256, the machine). A run folder is never overwritten: a new run is a new date.
The tree must be clean (the commit in `run.json` must name the code that ran) unless `--allow-dirty`.

    uv run python -m tools.run --rescore runs/DATE     # score a committed run again from its prediction files only
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

from adapters.registry import ADAPTERS
from tools.bench import speed
from tools.sets.common import PREDICTIONS

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
SETS = ["doorplate-suite", "usaddress-tests", "libpostal-us", "senzing-us", "geocode-dev", "golden"]
CONVERT = [
    ["tools.sets.doorplate_suite", "--fetch"],
    ["tools.sets.usaddress_tests"],
    ["tools.sets.libpostal_us"],
    ["tools.sets.senzing_us"],
    ["tools.sets.geocode_dev"],
    ["tools.sets.golden"],
]


def sh(*mod_args: str) -> None:
    cmd = [sys.executable, "-m", *mod_args]
    print("$ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def step(n: int, total: int, label: str) -> None:
    print(f"##progress step={n}/{total} label={label}", flush=True)


def prepare(stamp: str, allow_dirty: bool) -> Path:
    out = RUNS / stamp
    if out.exists():
        sys.exit(f"{out} exists: a run folder is never overwritten (use a new --date)")
    if git("status", "--porcelain") and not allow_dirty:
        sys.exit("the working tree is not clean: commit first, so run.json names the code that ran (or --allow-dirty)")
    return out


def full_run(stamp: str, skip_speed: bool, allow_dirty: bool) -> Path:
    out = prepare(stamp, allow_dirty)
    total = 6 if skip_speed else 7
    started = time.time()
    step(1, total, "fetch")
    sh("tools.sets.fetch")
    step(2, total, "convert")
    for args in CONVERT:
        sh(*args)
    shutil.rmtree(PREDICTIONS, ignore_errors=True)  # no prediction of an earlier run can slip in
    step(3, total, "predict")
    for name in SETS:
        sh("tools.sets.predict", name)
    problems = {}
    for meta in sorted(PREDICTIONS.glob("*/*.versions.json")):
        bad = json.loads(meta.read_text()).get("pin_problems")
        if bad:
            problems[f"{meta.parent.name}/{meta.name}"] = bad
    if problems:
        sys.exit(f"not the pinned parser build, run refused: {json.dumps(problems, indent=1)}")
    step(4, total, "copy predictions")
    out.mkdir(parents=True)
    shutil.copytree(PREDICTIONS, out / "predictions")
    step(5, total, "score")
    sh("scorer", "--predictions", str(out / "predictions"), "--out", str(out))
    if not skip_speed:
        step(6, total, "speed")
        sh("tools.bench.speed", "--out", str(out))
    step(total, total, "run.json")
    write_run_json(out, stamp, started, skip_speed)
    print(f"run written to {out}")
    return out


def write_run_json(out: Path, stamp: str, started: float, skip_speed: bool) -> None:
    versions = {}
    for name, cls in ADAPTERS.items():
        a = cls()
        versions[name] = a.versions()
        if hasattr(a, "close"):
            a.close()
    set_sha = {}
    for meta in sorted(out.glob("predictions/*/*.versions.json")):
        set_sha[meta.parent.name] = json.loads(meta.read_text())["set_sha256"]
    info = {
        "date": stamp,
        "commit": git("rev-parse", "HEAD"),
        "tree_clean": not git("status", "--porcelain"),
        "parser_versions": versions,
        "set_sha256": set_sha,
        "machine": speed.machine(),
        "speed_measured": not skip_speed,
        "seconds": round(time.time() - started),
    }
    (out / "run.json").write_text(json.dumps(info, indent=2) + "\n")


def rescore(run: Path) -> None:
    sh("tools.sets.fetch")
    for args in CONVERT:
        sh(*args)
    sh("scorer", "--predictions", str(run / "predictions"), "--out", str(run))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--skip-speed", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true")
    ap.add_argument(
        "--rescore", type=Path, help="rescore a committed run from its prediction files (overwrites its results)"
    )
    args = ap.parse_args(argv)
    if args.rescore:
        rescore(args.rescore)
    else:
        full_run(args.date, args.skip_speed, args.allow_dirty)
    return 0


if __name__ == "__main__":
    sys.exit(main())
