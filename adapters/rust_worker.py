"""Client for the Rust parser worker (`tools/rust-parsers`, one binary for the three Rust-only parsers).

Where the binary is: `$RUST_PARSERS_BIN`, default `tools/rust-parsers/target/release/rust-parsers`
(made by `cargo build --release --locked` in that folder).

Protocol, one JSON line each way: `{"strings": [...]}` in, `{"results": [{"fields": [[label, value], ...]} |
{"error": "..."}, ...]}` out. One worker process per parser; it is started on first use and again if it has stopped.
"""

import contextlib
import json
import os
import subprocess
from pathlib import Path

from adapters.base import Span, align

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BIN = ROOT / "tools" / "rust-parsers" / "target" / "release" / "rust-parsers"


def binary() -> Path:
    return Path(os.environ.get("RUST_PARSERS_BIN", DEFAULT_BIN))


def available() -> bool:
    return binary().exists()


class RustWorker:
    def __init__(self, parser: str):
        self.parser = parser
        self._proc = None

    def _start(self):
        if not available():
            raise RuntimeError(
                f"no Rust worker at {binary()}: run cargo build --release --locked in tools/rust-parsers"
            )
        # An empty working directory, so that no parser finds a config file of its own (addrust reads `.addrust.toml`).
        self._proc = subprocess.Popen(
            [str(binary()), "--parser", self.parser],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            cwd="/",
        )

    def _ask(self, texts: list[str]) -> list[dict]:
        if self._proc is None or self._proc.poll() is not None:
            self._start()
        self._proc.stdin.write(json.dumps({"strings": texts}) + "\n")
        self._proc.stdin.flush()
        line = self._proc.stdout.readline()
        if not line:
            raise RuntimeError(f"the {self.parser} worker stopped")
        return json.loads(line)["results"]

    def parse_many(self, texts: list[str]) -> list[list[tuple[str, str]] | None]:
        """`[label, value]` pairs per string, or None where the parser found nothing usable."""
        try:
            results = self._ask(texts)
        except (RuntimeError, BrokenPipeError, ValueError):
            self.close()  # one restart; a second failure is raised
            results = self._ask(texts)
        return [[tuple(f) for f in r["fields"]] if "fields" in r else None for r in results]

    def close(self):
        if self._proc is not None:
            with contextlib.suppress(OSError):
                self._proc.stdin.close()
            self._proc.kill()
            self._proc.wait()
            self._proc = None


def place_fields(text: str, fields) -> list[Span]:
    """Character spans for `(label, value)` fields that carry no positions, in the order of the text.

    The crates return their fields in a fixed order, not the order of the text, and often rewrite the values (upper
    case, `STREET` for `St`). So each value is looked for on its own, ignoring case, as whole words, in what is left
    of the text (characters already taken are blanked); a word that is not in the input is skipped, and a field of
    several words spans from its first found word to its last. A several-word field can run over a field found inside
    it (a crate may fold the city and state into the street name): the span that starts first is kept and the one it
    covers is dropped.
    """
    left, spans = text, []
    for label, value in fields:
        for sp in align(left, [(value, label)], ignore_case=True, skip_missing=True):
            spans.append(sp)
            left = left[: sp.start] + "\0" * (sp.end - sp.start) + left[sp.end :]
    spans.sort(key=lambda sp: sp.start)
    kept: list[Span] = []
    for sp in spans:
        if not kept or sp.start >= kept[-1].end:
            kept.append(sp)
    return kept
