#!/usr/bin/env python3
"""doorplate release appendix (issue #50): the doorplate adapter on the highest point release of each minor version.

    uv run python -m tools.releases [--versions 0.3.1 0.6.2] [--reference runs/2026-11-16] [--skip-speed]
    uv run python -m tools.releases --table        # only rebuild runs/doorplate-releases/releases.md

Releases come from PyPI (abi3 wheels, nothing is built): the highest X.Y.Z of every X.Y, so 0.3.1 stands for 0.3.x and
0.3.0 is not run. A release that already has a folder is skipped, so a rerun after a new release only adds that one.
Each release runs in its own throwaway environment (`/tmp/doorplate-releases/`, deleted afterwards): the
project's locked
dependencies plus `doorplate==X`. The doorplate adapter is run on every set; each set's SHA-256 must equal the reference
run's (else the reused usaddress and libpostal predictions would not match the sets, and the release is refused). The
Parser Score is computed by the scorer on a folder made of that release's doorplate files plus the reference run's
usaddress and libpostal files, exactly as in a pinned run. usaddress and libpostal are never rerun.

Writes `runs/doorplate-releases/<version>/` (`predictions/<set>/doorplate.*`, `results.md|json`, `speed.md|json`,
`release.json`) and `runs/doorplate-releases/releases.md` (one row per release; reads the folders only).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from tools.bench import speed
from tools.run import CONVERT, SETS, step
from tools.sets.common import PREDICTIONS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "doorplate-releases"
SCRATCH = Path("/tmp/doorplate-releases")
PARTS = [("golden/normal", "golden normal"), ("golden/hard", "golden hard"), ("golden/nightmare", "golden nightmare")]


def vkey(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def highest_per_minor() -> list[str]:
    with urllib.request.urlopen("https://pypi.org/pypi/doorplate/json", timeout=30) as r:
        rels = json.load(r)["releases"]
    best: dict[tuple[int, ...], str] = {}
    for v, files in rels.items():
        if not re.fullmatch(r"\d+\.\d+\.\d+", v) or not files or all(f.get("yanked") for f in files):
            continue
        k = vkey(v)[:2]
        if k not in best or vkey(v) > vkey(best[k]):
            best[k] = v
    return [best[k] for k in sorted(best)]


def run(cmd: list[str], env: dict | None = None) -> None:
    print("$ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True, env=env)


def ensure_sets(reference: Path) -> dict[str, str]:
    """Converted sets under build/sets/, checked against the reference run's SHA-256s."""
    want = json.loads((reference / "run.json").read_text())["set_sha256"]
    from tools.sets.common import set_path, sha256

    if not all(set_path(s).exists() for s in SETS):
        run([sys.executable, "-m", "tools.sets.fetch"])
        for args in CONVERT:
            run([sys.executable, "-m", *args])
    got = {s: sha256(set_path(s)) for s in SETS}
    bad = [s for s in SETS if got[s] != want[s]]
    if bad:
        sys.exit(f"sets differ from {reference.name}/run.json: {bad}; the reused predictions would not match")
    return got


def make_env(version: str) -> Path:
    env_dir = SCRATCH / f"env-{version}"
    shared = dict(os.environ, UV_PROJECT_ENVIRONMENT=str(env_dir))
    run(["uv", "sync", "--frozen", "--no-dev", "--quiet"], shared)
    py = env_dir / "bin" / "python"
    run(["uv", "pip", "install", "--quiet", "--python", str(py), f"doorplate=={version}"])
    return py


def one_release(version: str, reference: Path, sha: dict[str, str], skip_speed: bool) -> None:
    out = OUT / version
    py = make_env(version)
    shutil.rmtree(PREDICTIONS, ignore_errors=True)
    for s in SETS:
        run([str(py), "-m", "tools.sets.predict", s, "--parsers", "doorplate"])
    metas = {s: json.loads((PREDICTIONS / s / "doorplate.versions.json").read_text()) for s in SETS}
    versions = {m["versions"]["doorplate"] for m in metas.values()}
    if versions != {version}:
        sys.exit(f"installed doorplate is {versions}, not {version}")
    if any(metas[s]["set_sha256"] != sha[s] for s in SETS):
        sys.exit("a set changed during the run")
    out.mkdir(parents=True)
    shutil.copytree(PREDICTIONS, out / "predictions")
    score_dir(out, reference)
    if not skip_speed:
        run([str(py), "-m", "tools.bench.speed", "--parsers", "doorplate", "--out", str(out)])
    info = {
        "doorplate": version,
        "source": "PyPI wheel (abi3)",
        "reference_run": reference.name,
        "set_sha256": sha,
        "host": speed.machine(),
        "speed_measured": not skip_speed,
    }
    (out / "release.json").write_text(json.dumps(info, indent=2) + "\n")
    shutil.rmtree(SCRATCH / f"env-{version}", ignore_errors=True)


def score_dir(out: Path, reference: Path) -> None:
    """Score a release folder: its doorplate files plus the reference run's usaddress and libpostal files."""
    with tempfile.TemporaryDirectory() as td:
        pred = Path(td) / "predictions"
        for s in SETS:
            (pred / s).mkdir(parents=True)
            for f in (out / "predictions" / s).glob("doorplate.*"):
                shutil.copy(f, pred / s / f.name)
            for p in ("usaddress", "libpostal"):
                for f in (reference / "predictions" / s).glob(f"{p}.*"):
                    shutil.copy(f, pred / s / f.name)
        run([sys.executable, "-m", "scorer", "--predictions", str(pred), "--out", str(out)])


def table(reference: Path) -> str:
    def score_row(md: str, parser: str) -> tuple[str, str]:
        m = re.search(rf"^\| {parser} \| ([^|]+) \| ([^|]+) \|$", md.split("## Parser Score")[1], re.M)
        return m.group(1).strip(), m.group(2).strip()

    def acc(res: dict, parser: str, key: str) -> str:
        r = res[key][parser]
        return f"{100 * r['correct'] / r['records']:.1f}"

    rows, ref_md = [], (reference / "results.md").read_text()
    ref_res = json.loads((reference / "results.json").read_text())
    ref_speed = json.loads((reference / "speed.json").read_text())["parsers"]
    for d in sorted((p for p in OUT.iterdir() if p.is_dir()), key=lambda p: vkey(p.name)):
        md, res = (d / "results.md").read_text(), json.loads((d / "results.json").read_text())
        ps, f1 = score_row(md, "doorplate")
        cells = [d.name, ps, f1, *(acc(res, "doorplate", k) for k, _ in PARTS)]
        sp = d / "speed.json"
        if sp.exists():
            s = json.loads(sp.read_text())["parsers"]["doorplate"]
            cells += [f"{s['one']['per_second']:,.0f}", f"{s['4']['per_second']:,.0f}", f"{s['install_mb']:.1f}"]
        else:
            cells += ["-", "-", "-"]
        rows.append("| " + " | ".join(cells) + " |")
    ref_rows = []
    for p in ("usaddress", "libpostal"):
        ps, f1 = score_row(ref_md, p)
        s = ref_speed[p]
        ref_rows.append(
            f"| {p} {ref_res and json.loads((reference / 'run.json').read_text())['parser_versions'][p][p][:10]} "
            f"(from {reference.name}) | {ps} | {f1} | "
            + " | ".join(acc(ref_res, p, k) for k, _ in PARTS)
            + f" | {s['one']['per_second']:,.0f} | {s['4']['per_second']:,.0f} | {s['install_mb']:,.1f} |"
        )
    head = [
        "# doorplate releases on the showdown (appendix)",
        "",
        "The doorplate adapter on the highest point release of each minor version, on the sets and gold of "
        f"`{reference.name}`. Made by `uv run python -m tools.releases`; a release with a folder here "
        "is not run again.",
        "",
        "| Release | Parser Score (95% interval) | Field F1 score (95% interval) | "
        + " | ".join(f"{label} accuracy" for _, label in PARTS)
        + " | Strings/s, 1 process | Strings/s, 4 processes | Install MB |",
        "|---|---|---|" + "---|" * (len(PARTS) + 3),
    ]
    return "\n".join([*head, *rows, *ref_rows, ""]) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--versions", nargs="+", help="default: the highest X.Y.Z of every minor on PyPI")
    ap.add_argument("--reference", type=Path, default=ROOT / "runs" / "2026-11-16")
    ap.add_argument("--skip-speed", action="store_true")
    ap.add_argument("--table", action="store_true", help="only rebuild releases.md")
    args = ap.parse_args(argv)
    reference = args.reference.resolve()
    if not args.table:
        todo = [v for v in (args.versions or highest_per_minor()) if not (OUT / v).exists()]
        print(f"releases to run: {todo or 'none'}", flush=True)
        if todo:
            sha = ensure_sets(reference)
            for i, v in enumerate(todo, 1):
                step(i, len(todo), v)
                one_release(v, reference, sha, args.skip_speed)
    (OUT).mkdir(parents=True, exist_ok=True)
    (OUT / "releases.md").write_text(table(reference))
    print(f"wrote {OUT / 'releases.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
