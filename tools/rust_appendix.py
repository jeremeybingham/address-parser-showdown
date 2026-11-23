#!/usr/bin/env python3
"""Rust parsers appendix (issue #55): address_parser, addrust and us_address_parser on the pinned run's sets.

    uv run python -m tools.rust_appendix [--reference runs/2026-11-23] [--skip-speed] [--out runs/rust-parsers]

Not a full run: doorplate, usaddress and libpostal are not rerun. The three Rust adapters are run on every set (each
set's SHA-256 must equal the reference run's, else the reused predictions would not match), their prediction files are
copied to `<out>/predictions/`, and the scorer scores them together with the reference run's doorplate, usaddress and
libpostal files, exactly as in a pinned run. Speed is measured for the three Rust parsers only (one worker binary,
through the Python adapter, so the figure includes the adapter's cost). Writes `<out>/results.md|json`,
`speed.md|json` and `run.json`; the page that reads them is `report/RUST-PARSERS.md`. An existing folder is never
overwritten.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from tools.bench import speed
from tools.releases import ensure_sets, run
from tools.run import SETS, git, step
from tools.sets.common import PREDICTIONS

ROOT = Path(__file__).resolve().parents[1]
RUST = ["address_parser", "addrust", "us_address_parser"]
REUSED = ["doorplate", "usaddress", "libpostal"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--reference", type=Path, default=ROOT / "runs" / "2026-11-23")
    ap.add_argument("--out", type=Path, default=ROOT / "runs" / "rust-parsers")
    ap.add_argument("--skip-speed", action="store_true")
    ap.add_argument("--speed-strings", type=int, default=20000, help="strings per speed pass")
    ap.add_argument("--speed-reps", type=int, default=3)
    ap.add_argument("--speed-only", action="store_true", help="add speed and run.json to an existing folder")
    args = ap.parse_args(argv)
    reference, out = args.reference.resolve(), args.out.resolve()
    if out.exists() != args.speed_only:
        sys.exit(f"{out} exists: remove it to rerun" if out.exists() else f"{out} does not exist: nothing to add to")
    sha = ensure_sets(reference)
    total = len(SETS) + (1 if args.skip_speed else 2)
    if not args.speed_only:
        predict_and_score(out, reference, sha, total)
    versions = {
        p: json.loads((out / "predictions" / "golden" / f"{p}.versions.json").read_text())["versions"] for p in RUST
    }
    if not args.skip_speed:
        step(total, total, "speed")
        cmd = [sys.executable, "-m", "tools.bench.speed", "--parsers", *RUST, "--out", str(out)]
        run([*cmd, "--strings", str(args.speed_strings), "--reps", str(args.speed_reps)])
    info = {
        "reference_run": reference.name,
        "commit": git("rev-parse", "HEAD"),
        "tree_clean": not git("status", "--porcelain"),
        "rust_parser_versions": versions,
        "reused_from_reference": REUSED,
        "set_sha256": sha,
        "host": speed.machine(),
        "speed_measured": not args.skip_speed,
        "speed_strings": None if args.skip_speed else args.speed_strings,
    }
    (out / "run.json").write_text(json.dumps(info, indent=2) + "\n")
    print(f"wrote {out}")
    return 0


def predict_and_score(out: Path, reference: Path, sha: dict, total: int) -> None:
    # a (set, parser) pair already in build/predictions is kept, so a run resumes; the set hash is checked below
    for i, s in enumerate(SETS, 1):
        step(i, total, f"predict {s}")
        todo = [p for p in RUST if not (PREDICTIONS / s / f"{p}.versions.json").exists()]
        if todo:
            run([sys.executable, "-m", "tools.sets.predict", s, "--parsers", *todo])
    for s in SETS:
        meta = json.loads((PREDICTIONS / s / "addrust.versions.json").read_text())
        if meta["set_sha256"] != sha[s]:
            sys.exit(f"set {s} changed during the run")
    out.mkdir(parents=True)
    shutil.copytree(PREDICTIONS, out / "predictions")
    step(len(SETS) + 1, total, "score")
    with tempfile.TemporaryDirectory() as td:
        pred = Path(td) / "predictions"
        for s in SETS:
            (pred / s).mkdir(parents=True)
            for p in RUST:
                for f in (out / "predictions" / s).glob(f"{p}.*"):
                    shutil.copy(f, pred / s / f.name)
            for p in REUSED:
                for f in (reference / "predictions" / s).glob(f"{p}.*"):
                    shutil.copy(f, pred / s / f.name)
        run(
            [
                sys.executable,
                "-m",
                "scorer",
                "--predictions",
                str(pred),
                "--parsers",
                ",".join([*REUSED, *RUST]),
                "--out",
                str(out),
            ]
        )


if __name__ == "__main__":
    sys.exit(main())
