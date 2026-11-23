"""`address_parser` 0.1.10 (Rust crate `address-parser`), through the worker in `tools/rust-parsers`.

What it cannot place: it normalizes its values (a street type to the USPS abbreviation, a direction to `N`/`NE`, a
state to the two-letter code), so a value that is not in the input as a whole word (`St` for `Street`, `E` for `East`)
is dropped from the spans. The ZIP and the four-digit extension come back as two fields; when only a hyphen or
space separates them in the input they are one `zip` span. The crate says "no parse" for a string it does not
accept (a PO box, an intersection, an empty string): that string has no spans.
Placement is `adapters.rust_worker.place_fields`.
"""

from adapters.base import Adapter, Mapping, Span
from adapters.rust_worker import RustWorker, place_fields

PARSER = "address_parser"
CRATE_VERSION = "0.1.10"  # pinned with `=` in tools/rust-parsers/Cargo.toml


class AddressParserAdapter(Adapter):
    name = "address_parser"
    cannot_cover = True  # values it rewrites are dropped, so not every character is labeled

    def __init__(self):
        self.mapping = Mapping(self.name)
        self._worker = RustWorker(PARSER)

    def parse_many(self, texts: list[str]) -> list[list[Span]]:
        return [
            [] if fields is None else self._spans(text, fields)
            for text, fields in zip(texts, self._worker.parse_many(texts), strict=True)
        ]

    def parse(self, text: str) -> list[Span]:
        return self.parse_many([text])[0]

    @staticmethod
    def _spans(text: str, fields) -> list[Span]:
        spans = place_fields(text, fields)
        out: list[Span] = []
        for sp in spans:
            prev = out[-1] if out else None
            if (
                sp.label == "plus4"
                and prev is not None
                and prev.label == "zip"
                and text[prev.end : sp.start] in ("-", " ", "")
            ):
                out[-1] = Span(prev.start, sp.end, "zip")
            else:
                out.append(sp)
        return out

    def versions(self) -> dict[str, str]:
        return {"address_parser": CRATE_VERSION}

    def close(self):
        self._worker.close()
