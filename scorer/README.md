# scorer

Span-based scoring (step 5, issue #6). The rules are in [`METHODOLOGY.md`](../METHODOLOGY.md) ("Scoring and the Parser
Score"); the weights and the bootstrap settings are in [`formula.toml`](formula.toml), merged before the first scored run.

```sh
uv run python -m scorer                      # every converted set in build/ with predictions in build/predictions/
uv run python -m scorer --parsers doorplate,usaddress --out runs/RUN/   # results.md and results.json
```

| Module | Does |
|---|---|
| `spans.py` | gold and predicted spans to the coarse and fine sets that are compared; the conventions; gold readings from a card's `alternatives` |
| `stats.py` | Wilson interval, F1, the paired bootstrap |
| `score.py` | per-record scoring, parts, the Parser Score, the sensitivity table |
| `formula.toml` | group and part weights, which parts are reported apart and why, bootstrap resamples and seed |

**Input.** A converted set (`build/sets/NAME.jsonl.gz`; the record format is in `tools/sets/README.md`) and its prediction
files. A record's `part` is what a figure is reported on. The golden set's export must carry `part` = its tier, and may
carry `alternatives` and `flag` (`non_address` or `ambiguous`; such a record goes to its own part, `tier/flag`, which is in
no score). A set or prediction file that is missing is named in the output and the Parser Score is then marked incomplete:
the golden set is not exported yet, so no figure here is the Parser Score until it is.

**Reading the output.** Every part is listed with its role (`scored`, or why it is reported apart). A prediction with an
`error` counts as no spans (a wrong record) and the count is shown.
