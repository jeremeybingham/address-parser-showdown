"""Gold and predicted spans to the sets that are compared: coarse and fine tracks, conventions applied alike to both.

A span is `(start, end, label)` over the record text with a canonical label (`schema/schema.toml`). Nothing here knows
which side (gold or parser) a span list came from, so a convention can never favor one.

Coarse track: every fine part is replaced by its coarse field, neighbouring spans of one field are joined, then the
conventions are applied. Fine track: leaf labels, then the conventions (a span in an accepted reading becomes one shared
label). Conventions are in `schema/conventions.toml`; the two here are implemented by hand, and a test checks that no
other convention is listed without code.
"""

from __future__ import annotations

import re
from itertools import product

from schema import coarse
from schema import labels as schema_labels

Span = tuple[int, int, str]

_GAP = {"unit": re.compile(r"[\s#]*")}  # a `#` between a unit's parts does not split it (hash-before-unit)
_SPACE = re.compile(r"\s*")
_LETTER = re.compile(r"[A-Za-z]")
LETTER = "convention:letter_after_number"  # the fine label both readings of a lone letter after the number share
MAX_READINGS = 64
IMPLEMENTED_CONVENTIONS = {"letter-after-number", "hash-before-unit"}


def parent_of(label: str) -> str:
    return coarse(label)


def leaves() -> set[str]:
    """Labels with no fine parts: the unit of the fine track."""
    known = schema_labels()
    parents = {v.parent for v in known.values() if v.parent}
    return {k for k in known if k not in parents}


def coarse_spans(text: str, spans: list[Span], scored: set[str]) -> set[Span]:
    """Coarse field spans of `spans` (labels outside `scored` dropped), with the conventions applied."""
    out: list[list] = []
    for s, e, lab in sorted(spans):
        if lab not in scored and parent_of(lab) not in scored:
            continue
        coarse = parent_of(lab)
        if coarse not in scored:
            continue
        if out and out[-1][2] == coarse and _GAP.get(coarse, _SPACE).fullmatch(text[out[-1][1] : s]):
            out[-1][1] = e
        else:
            out.append([s, e, coarse])
    # hash-before-unit: a leading `#` is never part of the unit
    fixed: list[list] = []
    for s, e, lab in out:
        if lab == "unit":
            s += len(text[s:e]) - len(text[s:e].lstrip("# \t"))
            if s >= e:
                continue
        fixed.append([s, e, lab])
    # letter-after-number: `123 B ELM ST` is house_number `123` and street `B ELM ST` in both readings
    for i, (s, e, lab) in enumerate(fixed[:-1]):
        nxt = fixed[i + 1]
        m = re.fullmatch(r"(.*\S)\s+([A-Za-z])", text[s:e])
        if lab == "house_number" and nxt[2] == "street" and m and _SPACE.fullmatch(text[e : nxt[0]]):
            letter = e - 1
            fixed[i][1] = s + m.end(1)
            nxt[0] = letter
    return {(s, e, lab) for s, e, lab in fixed}


def fine_spans(text: str, spans: list[Span], scored: set[str]) -> set[Span]:
    """Leaf spans of `spans` over `scored` (leaf labels only), with the conventions applied."""
    leaf = leaves()
    items: list[Span] = []
    for s, e, lab in sorted(s for s in spans if s[2] in leaf):
        if items and items[-1][2] == lab and _SPACE.fullmatch(text[items[-1][1] : s]):
            items[-1] = (
                items[-1][0],
                e,
                lab,
            )  # one span per run of a label: the way a parser splits words is not scored
        else:
            items.append((s, e, lab))
    out: list[Span] = []
    for idx, (s, e, lab) in enumerate(items):
        prev = items[idx - 1] if idx else None
        after_number = prev is not None and prev[2] == "house_number_value" and _SPACE.fullmatch(text[prev[1] : s])
        if lab == "unit_type" and text[s:e] == "#":
            continue  # hash-before-unit: the `#` may be left unlabeled
        if lab == "unit_value" and text[s:e].startswith("#"):
            s += len(text[s:e]) - len(text[s:e].lstrip("# \t"))
            if s >= e:
                continue
        if after_number and lab == "house_number_suffix" and e - s == 1 and _LETTER.fullmatch(text[s:e]):
            out.append((s, e, LETTER))
        elif (
            after_number
            and lab == "street_name"
            and _LETTER.fullmatch(text[s])
            and (e - s == 1 or text[s + 1].isspace())
        ):
            out.append((s, s + 1, LETTER))  # the letter alone; the rest of the name follows
            rest = s + 1 + (len(text[s + 1 : e]) - len(text[s + 1 : e].lstrip()))
            if rest < e:
                out.append((rest, e, lab))
        else:
            out.append((s, e, lab))
    return {sp for sp in out if sp[2] == LETTER or sp[2] in scored}


def readings(spans: list[Span], alternatives: list[dict]) -> list[list[Span]]:
    """The gold readings of one record: the primary spans, and each way the alternatives can be chosen.

    An alternative `{"start", "end", "labels"}` lets the span `[start, end)` take any of `labels` (its primary label
    stays one choice); `none` leaves it unlabeled. A record with no alternatives has one reading.
    """
    if not alternatives:
        return [sorted(spans)]
    by_range = {(s, e): lab for s, e, lab in spans}
    ranges = {(a["start"], a["end"]) for a in alternatives}
    base = [sp for sp in spans if (sp[0], sp[1]) not in ranges]
    choices = []
    for a in alternatives:
        key = (a["start"], a["end"])
        opts = list(dict.fromkeys([by_range[key]] * (key in by_range) + a["labels"]))
        if key not in by_range and "none" not in opts:
            opts.append("none")
        choices.append([(key[0], key[1], o) for o in opts])
    out = []
    for combo in product(*choices):
        out.append(sorted(base + [c for c in combo if c[2] != "none"]))
        if len(out) >= MAX_READINGS:
            break
    return out
