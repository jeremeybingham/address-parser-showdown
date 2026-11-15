#!/usr/bin/env python3
"""Speed, load time, memory and install size of every adapter's parser (step 6, issue #7).

    uv run python -m tools.bench.speed [--strings 100000] [--reps 5] [--procs 4] [--out DIR] [--parsers ...]

Inputs: the shipped golden set's strings (invented values), repeated to `--strings` (default 100,000). Each parser is
measured in fresh processes (`worker.py`): one process on all the strings, and `--procs` processes started together on
equal shares. A figure is the median of `--reps` passes (the time of a pass is the slowest process's), with the fastest
and slowest pass beside it. Load time is the import plus the first parse (the slowest process). Memory is the resident
set of the one-process run after loading and after all the strings; with several processes it is the total
proportional set size after loading, so shared model pages count once. Install size is the files of the parser's
packages (libpostal: its library and model data). Speed and cost never enter the Parser Score. Writes `speed.md` and
`speed.json` to `--out` when given. The reference profile is 4 CPUs and 8 GB: the machine is named in the output, and
a run on other hardware says so.
"""

# ruff: noqa: E501
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
from importlib import metadata
from pathlib import Path

from adapters import libpostal_parser
from adapters.registry import ADAPTERS
from tools.sets.common import read_jsonl, set_path

WORKER = Path(__file__).with_name("worker.py")
REFERENCE = "4 CPUs, 8 GB"


def machine() -> str:
    cpu = "unknown CPU"
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    mem = next(
        (
            int(ln.split()[1]) / 1024 / 1024
            for ln in Path("/proc/meminfo").read_text().splitlines()
            if ln.startswith("MemTotal")
        ),
        0,
    )
    return f"{cpu}; {len(os.sched_getaffinity(0))} of {os.cpu_count()} CPUs usable and {mem:.0f} GB visible; {platform.system()} {platform.release()}; Python {platform.python_version()}"


def python_for(parser: str) -> tuple[list[str], dict]:
    if parser == "libpostal":
        h = libpostal_parser.home()
        return [str(h / "venv" / "bin" / "python")], dict(os.environ, LD_LIBRARY_PATH=str(h / "install" / "lib"))
    return [sys.executable], dict(os.environ)


def pss_mb(pid: int) -> float:
    try:
        for line in Path(f"/proc/{pid}/smaps_rollup").read_text().splitlines():
            if line.startswith("Pss:"):
                return int(line.split()[1]) / 1024
    except OSError:
        pass
    return 0.0


def run_workers(parser: str, texts: list[str], procs: int, reps: int, tmp: Path) -> dict:
    size = -(-len(texts) // procs)
    cmd, env = python_for(parser)
    ps = []
    for i in range(procs):
        f = tmp / f"{parser}-{procs}-{i}.json"
        f.write_text(json.dumps(texts[i * size : (i + 1) * size]))
        ps.append(
            subprocess.Popen(
                [*cmd, "-I", str(WORKER), parser, str(f), str(reps)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                env=env,
                text=True,
            )
        )
    for p in ps:
        if p.stdout.readline().strip() != "READY":
            raise RuntimeError(f"a {parser} worker did not start")
    pss = sum(pss_mb(p.pid) for p in ps)
    for p in ps:
        p.stdin.write("GO\n")
        p.stdin.flush()
    res = [json.loads(p.stdout.readline()) for p in ps]
    for p in ps:
        p.wait()
    passes = [max(r["passes"][k] for r in res) for k in range(reps)]
    return {
        "procs": procs,
        "passes": passes,
        "load_seconds": max(r["load_seconds"] for r in res),
        "rss_after_load_mb": max(r["rss_after_load_mb"] for r in res),
        "rss_after_parses_mb": max(r["rss_after_parses_mb"] for r in res),
        "pss_total_after_load_mb": pss,
    }


def dir_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def install_bytes(parser: str) -> tuple[int, str]:
    if parser == "libpostal":
        h = libpostal_parser.home()
        return dir_size(h / "install") + dir_size(h / "data"), "libpostal library and model data"
    top = {"doorplate": ["doorplate"], "usaddress": ["usaddress"]}[parser]
    seen, todo, total = set(), list(top), 0
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        try:
            dist = metadata.distribution(name)
        except metadata.PackageNotFoundError:
            continue
        total += sum((dist.locate_file(f)).stat().st_size for f in dist.files or [] if (dist.locate_file(f)).is_file())
        for r in dist.requires or []:
            if "extra ==" not in r:
                todo.append(r.split(";")[0].split(">")[0].split("=")[0].split("<")[0].split("[")[0].strip())
    return total, "package and required packages: " + ", ".join(sorted(seen))


def summarize(passes: list[float], n: int) -> dict:
    med = statistics.median(passes)
    return {"per_second": n / med, "median_s": med, "fastest_s": min(passes), "slowest_s": max(passes)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strings", type=int, default=100_000)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--parsers", nargs="+", choices=sorted(ADAPTERS), default=sorted(ADAPTERS))
    ap.add_argument(
        "--cpus", type=int, default=4, help="pin the run to this many CPUs (the reference profile's 4); 0 = no pinning"
    )
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    if args.cpus and hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[: args.cpus])  # inherited by the workers
    base = [r["text"] for r in read_jsonl(set_path("golden"))]
    texts = (base * (args.strings // len(base) + 1))[: args.strings]
    results = {
        "machine": machine(),
        "reference_profile": REFERENCE,
        "strings": len(texts),
        "distinct": len(base),
        "reps": args.reps,
        "parsers": {},
    }
    with tempfile.TemporaryDirectory() as td:
        for parser in args.parsers:
            adapter = ADAPTERS[parser]()
            one = run_workers(parser, texts, 1, args.reps, Path(td))
            many = run_workers(parser, texts, args.procs, args.reps, Path(td))
            size, what = install_bytes(parser)
            results["parsers"][parser] = {
                "versions": adapter.versions(),
                "one": {**one, **summarize(one["passes"], len(texts))},
                f"{args.procs}": {**many, **summarize(many["passes"], len(texts))},
                "install_mb": size / 1024 / 1024,
                "install_what": what,
            }
            print(f"##progress step={len(results['parsers'])}/{len(args.parsers)} label={parser}", flush=True)
    md = render(results, args.procs)
    print(md)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "speed.md").write_text(md)
        (args.out / "speed.json").write_text(json.dumps(results, indent=2) + "\n")
    return 0


def render(r: dict, procs: int) -> str:
    n = r["strings"]
    P = r["parsers"]
    names = list(P)
    L = [
        "## Speed, load time, memory and install size",
        "",
        f"Machine: {r['machine']}. Reference profile: {r['reference_profile']}; a run on other hardware is not that profile.",
        f"Inputs: {n:,} strings (the shipped golden set's {r['distinct']:,} strings, repeated). A figure is the median of {r['reps']} passes; the range is the fastest to the slowest pass.",
        "Versions: " + "; ".join(", ".join(f"{k} {v}" for k, v in P[p]["versions"].items()) for p in names) + ".",
        "",
        "| | " + " | ".join(names) + " |",
        "|---|" + "---|" * len(names),
    ]

    def row(label, fn):
        L.append(f"| {label} | " + " | ".join(fn(P[p]) for p in names) + " |")

    row(
        "Strings per second, one process",
        lambda d: (
            f"{d['one']['per_second']:,.0f} ({n / d['one']['slowest_s']:,.0f} to {n / d['one']['fastest_s']:,.0f})"
        ),
    )
    row(
        f"Strings per second, {procs} processes",
        lambda d: (
            f"{d[str(procs)]['per_second']:,.0f} ({n / d[str(procs)]['slowest_s']:,.0f} to {n / d[str(procs)]['fastest_s']:,.0f})"
        ),
    )
    row("Load time (import and first parse)", lambda d: f"{d['one']['load_seconds']:.3f} s")
    row("Memory after loading, one process", lambda d: f"{d['one']['rss_after_load_mb']:,.0f} MB")
    row(f"Memory after {n:,} parses, one process", lambda d: f"{d['one']['rss_after_parses_mb']:,.0f} MB")
    row(
        f"Memory after loading, {procs} processes together (shared pages counted once)",
        lambda d: f"{d[str(procs)]['pss_total_after_load_mb']:,.0f} MB",
    )
    row("Install size", lambda d: f"{d['install_mb']:,.1f} MB")
    L += ["", "Install size covers: " + "; ".join(f"{p}: {P[p]['install_what']}" for p in names) + ".", ""]
    L.append(
        "Speed and cost are never folded into the Parser Score. Each call is the parser's own (`doorplate.parse_tokens`, `usaddress.parse`, `postal.parser.parse_address`), without the adapter's alignment; a process is one thread."
    )
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
