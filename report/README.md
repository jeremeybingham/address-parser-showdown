# report

| Report | Run | doorplate | Status |
|---|---|---|---|
| [`REPORT.md`](REPORT.md), [`REPORT.pdf`](REPORT.pdf) | [`runs/2026-11-23/`](../runs/2026-11-23/) | 0.7.1 | **latest** |
| [`REPORT-2026-11-16.md`](REPORT-2026-11-16.md), [`REPORT-2026-11-16.pdf`](REPORT-2026-11-16.pdf) | [`runs/2026-11-16/`](../runs/2026-11-16/) | 0.6.0 | v0.1.0 report, kept as published |

`REPORT.md` is always the latest research report; its section 6.5 says what changed since the one before. Earlier
reports are kept as they were published, named by their run date, and are never edited (their links into `runs/` still
work, since they sit in the same folder). When a new run gets a new report, first copy `REPORT.md` and `REPORT.pdf` to
`REPORT-<its run date>.md` and `.pdf` unchanged, then write the new one in `REPORT.md` and add a row above.

The report covers the parsers, the schema and conventions, how the golden set was made, labeled and adjudicated,
results with intervals, speed and cost, error analysis by shape, threats to validity, how to reproduce, references.
[`RELEASES.md`](RELEASES.md) is a short appendix: each doorplate release scored on the same sets.
[`RUST-PARSERS.md`](RUST-PARSERS.md) is another: the three Rust-only parsers scored on the `2026-11-23` sets, without a full run.

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
