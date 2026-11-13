#!/usr/bin/env python3
"""Run adapters on a converted set and write one prediction file per parser.

    uv run python -m tools.sets.predict doorplate-suite                 # every adapter
    uv run python -m tools.sets.predict doorplate-suite --parsers usaddress doorplate

Reads `build/sets/<set>.jsonl.gz`; writes `build/predictions/<set>/<parser>.jsonl.gz` (`id`, `native` spans in the
parser's own labels, `spans` in canonical labels, `error` the exception type when the parse failed) and
`<parser>.versions.json`. Prints counts and timings, never a record. Parser output is never shown while labeling: these
files are for the scorer, not for reading by hand before the golden set is labeled.
"""

from __future__ import annotations

import argparse
import json
import sys
import time

from adapters.registry import ADAPTERS
from tools.sets.common import PREDICTIONS, read_jsonl, set_path, sha256, write_jsonl

BATCH = 500


def predict(adapter, records: list[dict]):
    """Yield one prediction per record, in order. A failure in a batch falls back to one string at a time."""
    total = len(records)
    for i in range(0, total, BATCH):
        chunk = records[i : i + BATCH]
        try:
            results = [(spans, None) for spans in adapter.parse_many([r["text"] for r in chunk])]
        except Exception:  # noqa: BLE001 - find which strings failed, one by one
            results = []
            for r in chunk:
                try:
                    results.append((adapter.parse(r["text"]), None))
                except Exception as e:  # noqa: BLE001 - recorded as the exception type only
                    results.append(([], type(e).__name__))
        for r, (spans, err) in zip(chunk, results, strict=True):
            canon = adapter.mapping.to_canonical(spans)
            yield {
                "id": r["id"],
                "native": [[s.start, s.end, s.label] for s in spans],
                "spans": [[s.start, s.end, s.label] for s in canon],
                "error": err,
            }
        done = min(i + BATCH, total)
        print(f"##progress step={done}/{total} label={adapter.name}", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("set")
    ap.add_argument("--parsers", nargs="+", choices=sorted(ADAPTERS), default=sorted(ADAPTERS))
    args = ap.parse_args(argv)
    records = list(read_jsonl(set_path(args.set)))
    for name in args.parsers:
        adapter = ADAPTERS[name]()
        problems = getattr(adapter, "pin_problems", lambda: [])()
        t0 = time.perf_counter()
        preds = list(predict(adapter, records))
        secs = time.perf_counter() - t0
        if hasattr(adapter, "close"):
            adapter.close()
        out = PREDICTIONS / args.set / f"{name}.jsonl.gz"
        write_jsonl(out, preds)
        meta = {"set": args.set, "set_sha256": sha256(set_path(args.set)), "versions": adapter.versions()}
        meta |= {"pin_problems": problems, "records": len(preds), "seconds": round(secs, 1)}
        (out.parent / f"{name}.versions.json").write_text(json.dumps(meta, indent=2) + "\n")
        errors = sum(p["error"] is not None for p in preds)
        print(f"  pin problems: {problems or 'none'}")
        print(f"{args.set} / {name}: {len(preds)} records, {errors} errors, {secs:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
