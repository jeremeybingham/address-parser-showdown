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
files. A record's `part` is what a figure is reported on. The golden set's converted file (`tools/sets/golden.py`) carries `part` = its tier, and may
carry `alternatives`, `flag` (`schema.FLAGS`), `doubtful`, `rough` and `unscored`. A flagged record goes to its own
part, `tier/flag`; a rough or doubtful one to `tier/rough` or `tier/doubtful`; none of these is in the score. An
`unscored` region (`[start, end]`) is left out on both sides: a predicted span that touches one is not scored. A set or prediction file that is missing is named in the output and the Parser Score is then marked incomplete:
the golden set is not exported yet, so no figure here is the Parser Score until it is.

**Reading the output.** Every part is listed with its role (`scored`, or why it is reported apart) and the count of
records no parser reads right (a count only). A table lists, per scored part, the records held out of it by reason; a
share over `drop_warn_share` (`formula.toml`) is marked. The sensitivity table has a row with the doubtful records put
back in their tiers. A prediction with an
`error` counts as no spans (a wrong record) and the count is shown.
