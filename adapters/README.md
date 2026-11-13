# adapters

One module per parser, so that every parser is read the same way.

## Contract

An adapter (`adapters/base.py`, class `Adapter`) has:

- `parse(text) -> list[Span]`: character spans `Span(start, end, label)` with the parser's **own** labels, in order, not
  overlapping, so that `text[start:end]` is the labeled piece. Text the parser leaves unlabeled has no span. Spans are
  characters, not tokens, so the way a parser splits text does not decide the score. A comma or semicolon at the end of
  a token is not part of its span.
- `mapping`: `adapters/mappings/<name>.toml`, the parser's labels to the canonical labels in
  [`schema/`](../schema/README.md). A value is a label, or a table `{default, if_string_has, then}` when the reading
  depends on the other labels in the string (usaddress's `USPSBoxType` is a PO box type, or a route's box type when the
  string has a route label).
- `versions()`: what a figure must name (the parser's version; for libpostal the commit, the data checksum and the
  binding version).

`adapter.canonical(text)` gives the spans with canonical labels. `adapters/registry.py` lists the adapters.

| Adapter | Reads | Notes |
|---|---|---|
| `doorplate_parser.py` | `doorplate.parse_tokens` (its token labels, which are usaddress's names) aligned to the input | A blank input or an intersection is a `ParseError`: no spans |
| `usaddress_parser.py` | `usaddress.parse`, default model | |
| `libpostal_parser.py` | `parse_address` in libpostal's own virtualenv (`libpostal_worker.py`), tokens found in the input ignoring case | Needs the pinned build below |

## Conformance test

`adapters/conformance.py` (run by `tests/test_conformance.py`) checks every adapter on the invented strings in
`conformance_strings.txt`: spans in order and inside the string, every label in the mapping and mapped to a canonical
label, and, for the `cover` strings, every letter and digit inside a span. Failures are described without quoting the
string. The libpostal case is skipped when there is no build (CI); run it locally.

## Adding a parser

1. Write `adapters/<name>_parser.py` with an `Adapter` subclass. If the parser returns tokens, `base.align` turns
   `(token, label)` pairs into spans (it raises `AlignmentError` for a token it cannot find, without quoting the input).
2. List the parser's labels in `adapters/mappings/<name>.toml`, each mapped to a canonical label (`other` for what the
   schema does not hold; a coarse label if the parser does not split the field).
3. Add it to `adapters/registry.py` and to the parameter list in `tests/test_conformance.py`; add a mapping coverage test
   in `tests/test_schema_and_mappings.py` listing the parser's documented labels.
4. Pin the version (`versions()`), and add `tools/<name>/` if it needs a build.
5. Run `tools/check.sh`. Add a line to the table above and to `docs/README.md` if you add a page.

## Pinned libpostal

`tools/libpostal/pins.env` holds the commit, model (`senzing`, parser 1.2.0), binding version and the data checksum.
`tools/libpostal/build.sh [PREFIX]` builds exactly that (about 3 GB of data; default prefix `$LIBPOSTAL_HOME` or
`~/projects/libpostal-senzing`) and `build.sh --verify` checks an existing build's data and records the result in
`DATA_CHECKSUM.sha256`. `LibpostalAdapter.pin_problems()` lists any difference between the build in use and the pins. The
`Dockerfile` builds the whole stack in one image (not part of CI; not yet built).
