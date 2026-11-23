"""One measuring process (run with `python -I`; it imports only the parser, so it also runs in libpostal's virtualenv).

    worker.py PARSER STRINGS.json REPS

Loads the parser (timed: import plus the first parse), prints READY, waits for GO on stdin, then parses its strings REPS
times and prints one JSON line: load seconds, every pass's seconds, resident memory after loading and after the passes
(MB, from /proc), and the peak. The call timed is the parser's own call, the one its adapter makes, without alignment.
"""

import json
import resource
import sys
import time

CHILD = []  # the Rust worker process, when there is one: its memory counts too


def rss_mb() -> float:
    return _rss("self") + sum(_rss(p.pid) for p in CHILD)


def _rss(pid) -> float:
    with open(f"/proc/{pid}/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return 0.0


def load(name):
    if name == "doorplate":
        import doorplate

        def call(t):
            try:  # noqa: SIM105 - no imports beyond the parser here
                doorplate.parse_tokens(t)
            except doorplate.ParseError:
                pass

    elif name == "usaddress":
        import usaddress

        def call(t):
            usaddress.parse(t)

    elif name == "libpostal":
        from postal.parser import parse_address

        def call(t):
            parse_address(t)

    elif name in ("address_parser", "addrust", "us_address_parser"):
        import subprocess
        from pathlib import Path

        binary = Path(__file__).resolve().parents[1] / "rust-parsers" / "target" / "release" / "rust-parsers"
        proc = subprocess.Popen(
            [str(binary), "--parser", name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, cwd="/"
        )
        CHILD.append(proc)

        def call(texts):  # the adapter's own call: batches of 500 over the worker's JSON-lines protocol
            for i in range(0, len(texts), 500):
                proc.stdin.write(json.dumps({"strings": texts[i : i + 500]}) + "\n")
                proc.stdin.flush()
                json.loads(proc.stdout.readline())

        call.batch = True
        call(["1 Main St, Springfield, IL 62701"])
        return call
    else:
        raise SystemExit(f"unknown parser {name}")
    call("1 Main St, Springfield, IL 62701")  # models load on first use
    return call


def main():
    name, path, reps = sys.argv[1], sys.argv[2], int(sys.argv[3])
    with open(path) as f:
        texts = json.load(f)
    t0 = time.perf_counter()
    call = load(name)
    load_s = time.perf_counter() - t0
    after_load = rss_mb()
    print("READY", flush=True)
    sys.stdin.readline()
    passes = []
    for _ in range(reps):
        t = time.perf_counter()
        if getattr(call, "batch", False):
            call(texts)
        else:
            for s in texts:
                call(s)
        passes.append(time.perf_counter() - t)
    out = {
        "load_seconds": load_s,
        "passes": passes,
        "rss_after_load_mb": after_load,
        "rss_after_parses_mb": rss_mb(),
        "rss_peak_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        "strings": len(texts),
    }
    print(json.dumps(out), flush=True)


main()
