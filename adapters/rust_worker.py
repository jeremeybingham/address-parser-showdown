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
