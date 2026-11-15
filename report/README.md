# report

[`REPORT.md`](REPORT.md) (plain markdown) is the research report for v0.1.0, written from the pinned run
`runs/2026-11-16/`: the parsers, the schema and conventions, how the golden set was made, labeled and adjudicated,
results with intervals, speed and cost, error analysis by shape, threats to validity, how to reproduce, references.

Its figures come from the run's `results.md` and `speed.md`, plus two scripts: `tools/report/breakdown.py` (the golden
set by stratum and shape class, with paired tests) and `tools/label/direction.py` (which way adjudication moved the
gold; reads the private label log). A new run gets a new report section or a new report; figures are never edited by hand.
