"""`us_address_parser` 0.3.0 (Rust crate), through the worker in `tools/rust-parsers` (`adapters/rust_worker.py`).

What it cannot place: it has no city, state or ZIP field (they end up inside `street_name` or `unit_no`, or are left
out), and it upper-cases and normalizes its values, so a value that is not in the input (a spelled-out suffix, say) is
dropped from the spans. Values are found in the input ignoring case, as whole words; a field of several words spans
from its first word to its last. Fields are placed wherever they are found, in any order. A string the parser rejects
has no spans. Its one `direction` field has no position, so the adapter calls it `direction_pre` when it comes before
the street name and `direction_post` otherwise.
"""

from adapters.base import Adapter, Mapping, Span, align
from adapters.rust_worker import RustWorker

PARSER = "us_address_parser"
CRATE_VERSION = "0.3.0"  # pinned with `=` in tools/rust-parsers/Cargo.toml


class UsAddressParserAdapter(Adapter):
    name = "us_address_parser"
    cannot_cover = True  # no city/state/ZIP: the conformance check does not require every character to be labeled

    def __init__(self):
        self.mapping = Mapping(self.name)
        self._worker = RustWorker(PARSER)

    def parse_many(self, texts: list[str]) -> list[list[Span]]:
        out = []
        for text, fields in zip(texts, self._worker.parse_many(texts), strict=True):
            out.append([] if fields is None else self._spans(text, fields))
        return out

    def parse(self, text: str) -> list[Span]:
        return self.parse_many([text])[0]

    @staticmethod
    def _spans(text: str, fields) -> list[Span]:
        # The crate returns its fields in a fixed order, not the order of the text, so each is looked for on its own in
        # what is left of the text (characters already taken are blanked).
        left, spans = text, []
        for label, value in fields:
            found = align(left, [(value, label)], ignore_case=True, skip_missing=True)
            for sp in found:
                spans.append(sp)
                left = left[: sp.start] + "\0" * (sp.end - sp.start) + left[sp.end :]
        spans.sort(key=lambda sp: sp.start)
        # A several-word field can run over a field found inside it (the crate folds city and state into the street
        # name): the span that starts first is kept and the one it covers is dropped.
        spans = [
            sp
            for i, sp in enumerate(spans)
            if all(sp.start >= o.end or o.start >= sp.end or o.start > sp.start for o in spans[:i])
        ]
        name = next((s for s in spans if s.label == "street_name"), None)
        if name is None:
            return spans
        return [
            Span(s.start, s.end, "direction_pre" if s.start < name.start else "direction_post")
            if s.label == "direction"
            else s
            for s in spans
        ]

    def versions(self) -> dict[str, str]:
        return {"us_address_parser": CRATE_VERSION}

    def close(self):
        self._worker.close()
