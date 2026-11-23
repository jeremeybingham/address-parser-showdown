# Documentation

## Pages by topic

| Topic | Page |
|---|---|
| What the project is, layout | [`../README.md`](../README.md) |
| Fairness rules and method | [`../METHODOLOGY.md`](../METHODOLOGY.md) |
| Label schema and conventions | [`../schema/README.md`](../schema/README.md) |
| Adapters, the conformance test, how to add a parser, the pinned libpostal build | [`../adapters/README.md`](../adapters/README.md) |
| Hand labeling and adjudication tool | [`../tools/label/README.md`](../tools/label/README.md) |
| Sets and manifests | [`../sets/README.md`](../sets/README.md) |
| Converting the existing sets, running the adapters on them | [`../tools/sets/README.md`](../tools/sets/README.md) |
| The full run, `just all`, CI or a run folder | `tools/run.py` (docstring); `runs/README.md`; `.github/workflows/`; `AGENTS.md` |
| Speed, memory and install size (step 6) | `tools/bench/speed.py` (its docstring says the method); `runs/` holds the table from the pinned run |
| Scoring and the Parser Score | [`../scorer/README.md`](../scorer/README.md) |
| The research report and the scripts behind its extra figures (`tools/report/breakdown.py`, `tools/label/direction.py`) | [`../report/REPORT.md`](../report/REPORT.md) (the latest; earlier reports kept as published are listed in [`../report/README.md`](../report/README.md)); the PDF with charts [`../report/REPORT.pdf`](../report/REPORT.pdf) and its renderer `tools/report/pdf.py` ([`../report/README.md`](../report/README.md)) |
| Round 8 (`nightmare`) survey: covered and adjacent variants per class (issue #22) | [`research/nightmare-survey.md`](research/nightmare-survey.md) |
| doorplate releases appendix (issue #50): the table, method and caveats | [`../report/RELEASES.md`](../report/RELEASES.md); `tools/releases.py`; `runs/doorplate-releases/` |

## When you change something, check these

| You change | Check |
|---|---|
| A convention or a schema field | `schema/`; `METHODOLOGY.md`; every adapter mapping; the conformance test |
| An adapter or a pinned version | its mapping; the version pins; `runs/` (a new run, never an edit to an old one) |
| The labeling tool or the gold format | `tools/label/README.md`; `sets/golden/MANIFEST.md`; `sets/golden/COMPOSITION.md`; the scorer's reader |
| A set or its converter | its `MANIFEST.md` (counts, checksums); `sets/README.md`; `tools/sets/README.md` |
| The scorer or the formula | `METHODOLOGY.md` (a formula change after the first run is listed in the report) |
| Build commands, layout, CI | `AGENTS.md`; `CLAUDE.md`; `README.md`; this index |
| `report/REPORT.md` | rebuild `report/REPORT.pdf` (`uv run --group report python -m tools.report.pdf`) in the same commit |
| A page added, renamed or removed | this index |
