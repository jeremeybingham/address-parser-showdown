"""`addrust` (Rust, git commit `8e28a7e`, crate version 0.1.2), through the worker in `tools/rust-parsers`.

Default settings only: the shipped pipeline, no `.addrust.toml` (the worker runs in `/`, where there is none).

What it cannot place: addrust upper-cases and standardizes its values (`STREET`, `FIFTH`, `PO BOX`), so a value that is
not in the input as a whole word is dropped from the spans (a word of a several-word value that is missing is skipped).
It sometimes folds city, state and unit into `street_name`; those spans then cover the folded words as one street name.
It has no field for a route (`RR 2`), an intersection or a country. A string it finds nothing in has no spans.
Placement is `adapters.rust_worker.place_fields`.
"""

from adapters.base import Adapter, Mapping, Span
from adapters.rust_worker import RustWorker, place_fields

PARSER = "addrust"
COMMIT = "8e28a7e"  # pinned in tools/rust-parsers/Cargo.toml (not on crates.io)
CRATE_VERSION = "0.1.2"


class AddrustAdapter(Adapter):
    name = "addrust"
    cannot_cover = True  # values it rewrites are dropped, so not every character is labeled

    def __init__(self):
        self.mapping = Mapping(self.name)
        self._worker = RustWorker(PARSER)

    def parse_many(self, texts: list[str]) -> list[list[Span]]:
        return [
            [] if fields is None else place_fields(text, fields)
            for text, fields in zip(texts, self._worker.parse_many(texts), strict=True)
        ]

    def parse(self, text: str) -> list[Span]:
        return self.parse_many([text])[0]

    def versions(self) -> dict[str, str]:
        return {"addrust": f"{CRATE_VERSION}@{COMMIT} (default configuration)"}

    def close(self):
        self._worker.close()
