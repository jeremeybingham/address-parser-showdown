# address-parser-showdown

A neutral, repeatable comparison of US address parsers: [doorplate](https://github.com/jeremeybingham/doorplate),
[usaddress](https://github.com/datamade/usaddress) and [libpostal](https://github.com/openvenues/libpostal) to start
with, and any other parser that supplies an adapter.

The question it answers: given a one-line US address, which parser splits it into house number, street, unit, city,
state and ZIP correctly most often, on addresses that look like real data and not only on tidy examples? The answer is
meant to hold up for people choosing a parser and for the authors of the parsers compared.

## Status (2026-11-13): no scores yet, and why

**Nothing is scored yet, on purpose.** The scorer and the Parser Score formula are fixed before the first scored run,
and the first run waits for the hand-labeled golden set. The author is labeling it now, card by card, by hand; the
remaining work (scorer finishing, adjudication, the first pinned run, the report) depends on those labels, so it
proceeds as the labeling does.

| Piece | State |
|---|---|
| Label schema and conventions list | Done ([`schema/`](schema/README.md)) |
| Adapters for doorplate, usaddress and libpostal, with a conformance test and mapping tables | Done ([`adapters/`](adapters/README.md)); the libpostal build is pinned |
| Existing test sets brought in (doorplate's suite, usaddress's and libpostal's own tests, Senzing's US rows, the geocode benchmark) | Converted and runnable through every adapter ([`tools/sets/`](tools/sets/README.md)) |
| Golden set: design, sampling, difficulty tiers | Drawn: about 2,500 cards in ten rounds ([`sets/golden/`](sets/golden/COMPOSITION.md)) |
| **Golden set: hand labeling** | **In progress.** 416 cards labeled so far (round 1 shipped as [gold](sets/golden/gold/round-1.jsonl)); the rest are drawn and waiting. Rounds are published as each is finished |
| Scorer and Parser Score | Written ([`scorer/`](scorer/README.md)); the formula is being finalized against the sampling decisions |
| Blind adjudication, first full pinned run, speed and cost | Waiting for the labels |
| Research report | After the runs ([`report/`](report/README.md)) |

The plan and its step issues are in this repository's issues (milestone **v0.1.0**; start at the
[tracker, #1](https://github.com/jeremeybingham/address-parser-showdown/issues/1)).

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

About 2,500 records in ten rounds, mixing three kinds of text so no single source decides the result:

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
  remove it. The report will publish how often adjudication changed a label and in which direction.
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
| [`report/`](report/README.md) | The research report, written after the runs |
| [`docs/`](docs/README.md) | Index of all documentation |

## Adding your parser

Write an adapter (a string in, spans out), a mapping to the schema, and pass the conformance test; the steps are in
[`adapters/README.md`](adapters/README.md). Issues and PRs are welcome, including disagreements with a convention or a
mapping decision, which are written down so they can be argued with.

## License

Code: MIT ([`LICENSE`](LICENSE)). Data: per set, stated in each set's `MANIFEST.md`.
