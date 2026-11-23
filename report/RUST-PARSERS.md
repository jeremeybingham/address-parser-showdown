# Rust parsers on the showdown (appendix)

A short appendix to the [report](REPORT.md): `address_parser`, `addrust` and `us_address_parser`, the three Rust-only
parsers added in issue #55, scored on the sets and gold of the pinned run `2026-11-23`. It is not a full run and does not
change the report. A full report with these parsers waits for version 2.

**Method.** The three adapters ran on every set of the pinned run (every set's SHA-256 checked equal to that run's) and
were scored by the same scorer and formula (version 1) together with the `2026-11-23` predictions of doorplate 0.7.1,
usaddress and libpostal, reused unchanged, so only the three new parsers are new numbers. Versions: `address_parser`
0.1.10, `addrust` 0.1.2 at commit `8e28a7e` (default configuration, no config file), `us_address_parser` 0.3.0; one Rust
worker binary (`tools/rust-parsers/`, Rust 1.91.0). Everything is in `runs/rust-parsers/`; `uv run python -m
tools.rust_appendix` makes it (about 2 minutes, plus the speed step).

| Parser | Parser Score (95% interval) | Field F1 score (95% interval) | golden normal accuracy | golden hard accuracy | golden nightmare accuracy |
|---|---|---|---|---|---|
| doorplate 0.7.1 (reused) | 91.8 (90.7 to 92.9) | 97.9 (97.6 to 98.1) | 94.9 | 92.4 | 73.0 |
| usaddress 0.5.16 (reused) | 84.7 (83.4 to 86.0) | 95.7 (95.3 to 96.1) | 93.6 | 88.5 | 51.3 |
| libpostal 25099c5066 (reused) | 80.8 (79.5 to 82.2) | 93.4 (92.8 to 93.9) | 91.8 | 70.9 | 54.0 |
| address_parser 0.1.10 | 29.4 (28.1 to 30.7) | 75.6 (74.7 to 76.4) | 33.0 | 37.6 | 30.1 |
| addrust 0.1.2 | 24.0 (23.0 to 25.1) | 65.2 (64.4 to 65.9) | 35.6 | 11.3 | 15.9 |
| us_address_parser 0.3.0 | 0.0 (0.0 to 0.0) | 23.1 (22.8 to 23.4) | 0.0 | 0.0 | 0.0 |

Speed on the same machine, pinned to 4 CPUs (20,000 strings, median of 3 passes; the call is the one the adapter makes,
the Rust worker over its JSON-lines protocol in batches of 500, so the figure includes the worker and Python's
JSON handling):

| Parser | Strings/s, 1 process | Strings/s, 4 processes | Memory after loading, MB |
|---|---|---|---|
| address_parser | 36,424 | 91,764 | 21 |
| addrust | 6,953 | 20,823 | 26 |
| us_address_parser | 87,027 | 250,191 | 33 |
| doorplate 0.7.1 (from the pinned run `2026-11-23`, not remeasured) | 116,534 | 360,696 | 25 |

The three Rust parsers share one 4.3 MB worker binary, so install size does not separate them. The full tables
(per part, per field, fine track, sensitivity) are in `runs/rust-parsers/results.md` and `speed.md`.

## Reading the scores

These numbers measure the parser **and** what a span-based benchmark can credit it for. Read three things before quoting
a low figure.

- **They answer a different question.** The Parser Score is record accuracy: every field of a record must be right. A
  parser that does not return city, state and ZIP can never score on whole records. `us_address_parser` has no such
  fields (its crate's output is street number, direction, street name and type, unit), so its 0.0 is the schema's
  consequence, not a measurement of how well it parses what it does return. Its field F1 (23.1) and house-number F1
  (97 to 99 on most sets) show what it does. It is a street-line parser, not an address parser.
- **Normalized output cannot be placed.** The scorer needs each value's position in the input. `address_parser` returns
  `Dr` for `Drive` and `Ln` for `LANE`; `addrust` upper-cases and expands (`DRIVE`, `MAIN`). The adapters find a value in
  the input ignoring case and as a whole word, and drop what they cannot find. So a street type the parser got right
  (`Drive` read as `Dr`) is missing from the spans and the record is marked wrong. This is why `street` F1 on golden
  normal is 38.8 and 36.0 for these two against about 98 for the others. The effect is in the adapters (a possible fix,
  not made here: place a normalized value by its position, or match it against the street-suffix variants), not in the
  crates; how much of the gap it explains has not been measured.
- **Real failures are in there too.** `address_parser` answers "no parse" on a line without a state
  (`8298 Kaerfaes Ln, Hobart 98025`), and `addrust` then folds the city into the street name. `addrust` on
  `geocode-dev` finds almost no city, state or ZIP (0.0 F1): those lines have no commas, and it takes the whole tail as the street name and the ZIP as a unit.
  Those are parser behaviours on the inputs, as scored by the same rules as the other three.

## What the table says, and what it does not

- Ranking: doorplate, usaddress and libpostal are far ahead of the three; among the three, `address_parser` leads on the
  Parser Score (29.4 against 24.0), but `addrust` leads it on golden normal accuracy (35.6 against 33.0) and the two
  trade places with the weights (see the sensitivity table: dropping geocode-dev or the golden set reverses them). Call
  them level.
- The three are fast. `us_address_parser` is about as fast as doorplate in one process (87,000 against 117,000 strings
  a second), `address_parser` about a third of that, `addrust` about 6% of it.
- Nothing here changes the gold, the conventions or the formula.

## Caveats

- Adapter mappings are decisions (`adapters/mappings/`) and the normalization point above is a limit of the adapters.
  Treat the numbers as "as adapted", and rerun after any adapter change as a new folder, never an edit.
- A first version of the worker called `addrust::parse`, which rebuilds the parser's pipeline on every string (about 46
  strings a second). The worker now builds it once; the output is byte for byte the same on a set checked, and the
  numbers here are from the fixed worker.
- Speed is one session. doorplate's row is the pinned run's figure (100,000 strings, called without the worker), so compare orders of
  magnitude only.
- Version 2 of the report is where these parsers get the full treatment (per-class tables, paired tests, any adapter
  improvement).
