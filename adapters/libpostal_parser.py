"""libpostal (the pinned Senzing build), run in its own virtualenv by `libpostal_worker.py`.

Where the build is: `$LIBPOSTAL_HOME`, default `~/projects/libpostal-senzing` (made by `tools/libpostal/build.sh`).
libpostal lowercases what it returns, so its tokens are found in the input ignoring case.
"""

import json
import os
import subprocess
from pathlib import Path

from adapters.base import Adapter, Mapping, Span, align

ROOT = Path(__file__).resolve().parent.parent
PINS_FILE = ROOT / "tools" / "libpostal" / "pins.env"
WORKER = Path(__file__).with_name("libpostal_worker.py")


def pins() -> dict[str, str]:
    lines = (ln.strip() for ln in PINS_FILE.read_text().splitlines())
    return dict(ln.split("=", 1) for ln in lines if ln and not ln.startswith("#"))


def home() -> Path:
    return Path(os.environ.get("LIBPOSTAL_HOME", Path.home() / "projects" / "libpostal-senzing"))


def available() -> bool:
    return (home() / "venv" / "bin" / "python").exists()


class LibpostalAdapter(Adapter):
    name = "libpostal"

    def __init__(self):
        self.mapping = Mapping(self.name)
        self._proc = None

    def _start(self):
        h = home()
        if not available():
            raise RuntimeError(f"no libpostal build at {h}: run tools/libpostal/build.sh or set LIBPOSTAL_HOME")
        env = dict(os.environ, LD_LIBRARY_PATH=str(h / "install" / "lib"))
        self._proc = subprocess.Popen(
            [str(h / "venv" / "bin" / "python"), "-I", str(WORKER)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            env=env,
            text=True,
        )

    def parse_many(self, texts: list[str]) -> list[list[Span]]:
        if self._proc is None or self._proc.poll() is not None:
            self._start()
        self._proc.stdin.write(json.dumps({"strings": texts}) + "\n")
        self._proc.stdin.flush()
        line = self._proc.stdout.readline()
        if not line:
            raise RuntimeError("the libpostal worker stopped")
        results = json.loads(line)["results"]
        return [align(t, [tuple(p) for p in r], ignore_case=True) for t, r in zip(texts, results, strict=True)]

    def parse(self, text: str) -> list[Span]:
        return self.parse_many([text])[0]

    def versions(self) -> dict[str, str]:
        """What the build says about itself; `pin_problems` compares it with `pins.env`."""
        h = home()

        def read(name, index):
            words = (h / name).read_text().split() if (h / name).exists() else []
            return words[index] if words else "unknown"

        return {
            "libpostal": read("LIBPOSTAL_COMMIT.txt", 0),
            "data_checksum": read("DATA_CHECKSUM.sha256", 0),
            "pypostal": read("POSTAL_VERSION.txt", -1),
        }

    def pin_problems(self) -> list[str]:
        """Differences between the build in use and `pins.env` (empty when it is the pinned build)."""
        p, v = pins(), self.versions()
        pairs = [
            ("libpostal commit", v["libpostal"], p["LIBPOSTAL_COMMIT"]),
            ("data checksum", v["data_checksum"], p["LIBPOSTAL_DATA_CHECKSUM"]),
            ("pypostal", v["pypostal"], p["PYPOSTAL_VERSION"]),
        ]
        return [f"{what}: have {have}, pinned {want}" for what, have, want in pairs if have != want]

    def close(self):
        if self._proc is not None:
            self._proc.stdin.close()
            self._proc.wait()
            self._proc = None
