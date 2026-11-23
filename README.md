# address-parser-showdown

A neutral, repeatable comparison of US address parsers: [doorplate](https://github.com/jeremeybingham/doorplate),
[usaddress](https://github.com/datamade/usaddress) and [libpostal](https://github.com/openvenues/libpostal) to start
with, and any other parser that supplies an adapter.

The question it answers: given a one-line US address, which parser splits it into house number, street, unit, city,
state and ZIP correctly most often, on addresses that look like real data and not only on tidy examples? The answer is
meant to hold up for people choosing a parser and for the authors of the parsers compared.

## Status (2026-11-23): initial result, rerun with doorplate 0.7.1

**The full pinned run is done, and was rerun on 2026-11-23 with doorplate 0.7.1.** The golden set is labeled and adjudicated (2,439 shipped records), the scorer and
the pre-registered Parser Score formula are fixed, and all three parsers were run at pinned versions. This is an
**initial result**: one labeler, one golden set, one reference machine, and doorplate's author wrote the golden set and the
report. Read it with the limitations below, and treat the ranking as a first measurement to be checked, not a verdict.

Full report: **[`report/REPORT.md`](report/REPORT.md)**, also as a typeset PDF with charts:
**[`report/REPORT.pdf`](report/REPORT.pdf)** (earlier reports, kept as published, are listed in [`report/README.md`](report/README.md)). Both are written from the pinned run
[`runs/2026-11-23/`](runs/2026-11-23/) (tables in its [`results.md`](runs/2026-11-23/results.md) and
[`speed.md`](runs/2026-11-23/speed.md)). doorplate 0.7.1, usaddress 0.5.16 and libpostal (Senzing model 1.2.0), all at
default settings. The v0.1.0 run [`runs/2026-11-16/`](runs/2026-11-16/) (doorplate 0.6.0) is kept; usaddress's and
libpostal's predictions are byte-identical in both runs (report section 6.5).

### Summary of the initial result

| | doorplate | usaddress | libpostal |
|---|---|---|---|
| **Parser Score** (95% interval) | **91.8** (90.7 to 92.9) | **84.7** (83.4 to 86.0) | **80.8** (79.5 to 82.2) |
| Golden set, `normal` / `hard` / `nightmare` | 94.9 / 92.4 / 73.0 | 93.6 / 88.5 / 51.3 | 91.8 / 70.9 / 54.0 |
| Golden set, random public stratum (829 records) | 93.7 | 93.0 | 91.3 |
| Strings per second, one process | 116,534 | 8,947 | 15,565 |
| Memory after loading, one process | 25 MB | 27 MB | 2,958 MB |

The Parser Score is coarse record accuracy (a record is right when every house number, street, unit, PO box, route,
city, state and ZIP span matches), half on the golden set's three tiers and half on four neutral outside sets. Speed
and cost are never part of it.

- **The ranking is doorplate, then usaddress, then libpostal.** It holds in every sensitivity row, including with each
  set left out and with equal weights.
- **On ordinary public address lines the three are close.** On the random public stratum, doorplate and usaddress cannot
  be told apart at this size (exact McNemar p = 0.29); libpostal is behind both (p < 0.001 and p = 0.04). Most of the
  Parser Score's spread comes from rarer shapes: rural routes, military lines, units in unusual places and typos.
- **Each parser leads on its own home test set**, which is why the home sets are reported apart and kept out of the
  headline.
- **A scoring fault was fixed after the first run** (the 2026-11-15 run is kept unchanged; its Parser Scores were
  86.0, 80.2 and 76.0). The prediction files are byte-identical; only the scorer and 140 highway cards changed, and the
  ranking did not. The report's section 6.4 gives the details.
- **Cost:** doorplate is about five times faster than libpostal and eight times faster than usaddress in one process;
  libpostal needs about 3 GB of memory and disk where the other two need under 30 MB.

Not done yet: a second labeler or outside review of the gold, more parsers through the adapter route, and
later runs (each a new dated folder under `runs/`). The plan and its step issues are in this repository's issues
(milestone **v0.1.0**; start at the [tracker, #1](https://github.com/jeremeybingham/address-parser-showdown/issues/1)).

| Piece | State |
|---|---|
| Label schema and conventions list | Done ([`schema/`](schema/README.md)) |
| Adapters for doorplate, usaddress and libpostal, with a conformance test and mapping tables | Done ([`adapters/`](adapters/README.md)); the libpostal build is pinned |
| Adapters for three Rust-only parsers (`address_parser`, `addrust`, `us_address_parser`) | Done, conformance passes; not yet in a pinned run (tracker #49) |
| Existing test sets (doorplate's suite, usaddress's and libpostal's own tests, Senzing's US rows, the geocode benchmark) | Converted and scored ([`tools/sets/`](tools/sets/README.md)) |
| Golden set: design, sampling, hand labeling, blind adjudication | Done: 2,439 records in twelve rounds ([`sets/golden/`](sets/golden/COMPOSITION.md)) |
| Scorer and Parser Score | Done; formula version 1, fixed before the first run ([`scorer/`](scorer/README.md)) |
| Pinned run, speed and cost | Done: [`runs/2026-11-16/`](runs/2026-11-16/) (v0.1.0), [`runs/2026-11-23/`](runs/2026-11-23/) (doorplate 0.7.1) |
| Research report | Done: [`report/REPORT.md`](report/REPORT.md), and as a PDF with charts: [`report/REPORT.pdf`](report/REPORT.pdf) |

## How the comparison is kept fair

The full rules are in [`METHODOLOGY.md`](METHODOLOGY.md). The short version:

- **Labels never come from a parser.** The golden set is labeled by hand, with every parser's output hidden. Where a
  source has its own fields, those are used; a parser's guess is never a label.
- **Conventions are not errors.** Where reasonable readings differ (a letter after the house number, `#` before a
  unit, `EXT` after a street), the gold lists the accepted readings, each cited from USPS Publication 28 or a parser's
  own documentation, and the list is fixed before any scoring.
- **Spans, not tokens.** Predictions are compared as character spans, so how a parser splits words does not decide
  the score. Each parser's own labels are mapped to the neutral schema in a visible mapping file.
- **Score only what every parser claims to do** for the headline (house number, street, unit, PO box, route, city,
  state, ZIP). Finer labels are a separate track, reported apart.
- **Default settings, pinned versions.** No retraining or tuning; every figure names the parser versions and model
  checksums it came from, and every prediction file is committed so a result can be checked.
- **Home sets are disclosed.** A parser's own test files, or sets it was built near, are reported but kept out of
  that parser's aggregate.
- **Difficulty is fixed by shape, never by who fails.** Records are tiered `normal`, `hard` and `nightmare` by their
  shape before any run; tiers are reported separately and never averaged by record count. Records are never picked
  where parsers disagree, which is the mistake that made an earlier benchmark unfair to one parser.
- **A private twin of the golden set** (same recipe, unpublished seed) is kept outside the repository to catch
  tuning to the public set.
- **The formula is pre-registered.** The Parser Score weights are fixed in [`scorer/formula.toml`](scorer/formula.toml)
  before the first scored run; a later change is a PR that says why and is listed in the report. Speed and cost are
  never part of the score.

## How the golden set is made

About 2,400 records in twelve rounds, mixing three kinds of text so no single source decides the result:

- **Public records**, drawn at random by seeded hash from public sources (the National Address Database and messy
  business and license registries such as FMCSA, Texas TDLR, Virginia SCC, NY corporations, FCC amateur licenses, SBA
  PPP loans). This random stratum is the headline.
- **Hand templates** with invented values, covering real shapes: units, PO boxes, rural routes, highways, fractions,
  care-of, general delivery, typos, case and punctuation changes, and harder and "nightmare" classes paired as forms
  an existing rule covers and nearby forms it does not.
- **Clean ordinary forms**, as a ceiling check.

Public-record rows are labeled on their real text, so a hard card can be checked on a map. The text that ships is then
rebuilt from the labels with invented names and numbers of the same length, so **no real person's or business's
address is published**, and the shipped gold is the hand gold unchanged. Every record is also checked by string against
the training and test data of the parsers compared. Details: [`sets/golden/COMPOSITION.md`](sets/golden/COMPOSITION.md).

## Limitations, stated up front

- **Conflict of interest.** doorplate's author builds this repository and is the only labeler. The mitigations above
  (blind labeling, a pre-registered formula, a private twin, every prediction published) reduce this; they do not
  remove it. The report publishes how often adjudication changed a label and in which direction (section 6.3).
- **One labeler.** There is no second human labeler; this is a stated limitation, not hidden.
- **Not a work list.** The sets are not meant to be tuned against by any parser, doorplate included: a rule change
  needs a reason from another source.
- **Scope.** It checks how a string is split, not whether the address exists.

## What is here

| Folder | What |
|---|---|
| [`schema/`](schema/README.md) | The neutral label schema every parser's output is mapped to, and the conventions list |
| [`adapters/`](adapters/README.md) | One module per parser: a string in, character spans in the parser's own labels out, plus its mapping table. [How to add a parser](adapters/README.md) |
| [`sets/`](sets/README.md) | The test sets, each with a `MANIFEST.md` (source, license, counts, checksums) |
| [`scorer/`](scorer/README.md) | Span-based scoring, record accuracy, field F1 and the Parser Score |
| [`tools/`](docs/README.md) | Sampling, the blind labeling page, set converters, the pinned libpostal build |
| [`runs/`](runs/README.md) | Prediction files and results per pinned parser version |
| [`report/`](report/README.md) | The research report for the initial v0.1.0 result |
| [`docs/`](docs/README.md) | Index of all documentation |

## Adding your parser

Write an adapter (a string in, spans out), a mapping to the schema, and pass the conformance test; the steps are in
[`adapters/README.md`](adapters/README.md). Issues and PRs are welcome, including disagreements with a convention or a
mapping decision, which are written down so they can be argued with.

## License

Code: MIT ([`LICENSE`](LICENSE)). Data: per set, stated in each set's `MANIFEST.md`.
