# AGENTS.md

Guidance for AI coding agents and people working in this repository (tool-neutral).

`address-parser-showdown` compares US address parsers (doorplate, usaddress, libpostal, and any parser with an
adapter) on equal terms: a neutral label schema, a hand-labeled golden set, span-based scoring, one pinned and
repeatable run, and a report. It is for people choosing a parser and for parser authors. It is not a work list for any
parser, and it does not validate that an address exists.

## Finding things

| You want | Go to |
|---|---|
| What it is and the layout | `README.md` |
| The fairness rules | `METHODOLOGY.md` |
| The plan and what is in v0.1.0 | the tracker issue (milestone v0.1.0) and its step issues |
| All documentation by topic | `docs/README.md` |
| Current state and next step (local, git-ignored) | `local-data/SESSION.md` |

## Build and test

```sh
tools/check.sh            # the whole local gate (ruff, pytest); run before finishing any change
uv sync                   # the Python environment
just all                  # the full pinned run (not written yet)
```

## Rules that must hold

- No parser's output makes or changes a gold label; parser output is hidden while labeling (`METHODOLOGY.md`).
- The Parser Score formula and the conventions list are fixed in a PR before the first scored run; a later change is a
  PR that says why and is listed in the report.
- Every figure names the pinned parser versions and model checksums it came from; every prediction file is committed.
- Each set has a `MANIFEST.md` (source, license, counts, checksums); sets fetched by script are checked by checksum.
- Private data stays in `local-data/` (git-ignored). Examples, tests and the shipped golden set use invented or
  anonymized values only.
- Docs change in the same commit as the behavior they describe (`docs/README.md` lists what to check).

## Where things are

`schema/` label schema and conventions; `adapters/` one module per parser; `sets/` test sets and manifests; `scorer/`
scoring; `runs/` prediction files and results per run; `report/` the report; `tests/` pytest; `tools/` scripts
(`check.sh`); `docs/` documentation index; `local-data/` private data (git-ignored).
