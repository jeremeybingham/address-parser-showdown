# report

[`REPORT.md`](REPORT.md) (plain markdown) is the research report for the initial v0.1.0 result, written from the pinned run
`runs/2026-11-16/`: the parsers, the schema and conventions, how the golden set was made, labeled and adjudicated,
results with intervals, speed and cost, error analysis by shape, threats to validity, how to reproduce, references.

Its figures come from the run's `results.md` and `speed.md`, plus two scripts: `tools/report/breakdown.py` (the golden
set by stratum and shape class, with paired tests) and `tools/label/direction.py` (which way adjudication moved the
gold; reads the private label log). A new run gets a new report section or a new report; figures are never edited by hand.

[`REPORT.pdf`](REPORT.pdf) is the same report typeset for reading and printing: a cover with the headline scores, a
contents list, and eight figures (how a record is scored; the Parser Score with intervals; the sensitivity rows; each
scored part; the golden set by stratum; speed and cost; accuracy by shape class; the covered and adjacent `nightmare`
forms). The text and tables are REPORT.md unchanged. Each chart reads its numbers from the table it sits above, so the
PDF cannot disagree with the markdown. Rebuild it after any change to REPORT.md:

```sh
uv run --group report python -m tools.report.pdf          # writes report/REPORT.pdf (--html PATH also keeps the page)
```

It needs the `report` dependency group (matplotlib, markdown, playwright) and a Chromium binary: the Playwright build
under `~/.cache/ms-playwright`, or set `CHROMIUM`. Links in the PDF point to the files on GitHub.
