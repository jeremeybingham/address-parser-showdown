# Methodology

> **Status: draft.** These principles come from the plan (the v0.1.0 tracker issue). They are fixed before any parser
> is scored; a later change is made in a PR that says why, and is listed in the report.

## Fairness principles

- **No parser's output makes or changes a gold label.** Labels come from the source fields (where a source has them)
  and from the owner's review. Parser output is hidden while labeling.
- **Conventions are not errors.** Where reasonable readings differ (a letter after the house number, `EXT` after a
  street, a compass word that starts a city, `#` before a unit), the gold lists the accepted readings, and the list is
  fixed before any parser is scored. Each convention is cited from a source (USPS Publication 28, a parser's own docs
  or training data).
- **Score only what all parsers claim to do** for the headline. Finer labels (usaddress's pre-type and pre-modifier,
  doorplate's unit types) are scored on a separate track that is reported apart.
- **Score by character spans, not tokens**, so the way a parser splits text does not decide the score.
- **Default settings only**, no retraining, versions and model checksums pinned beside every figure.
- **Disclose what each parser was built near.** usaddress's and libpostal's own test files are regression sets for
  them; doorplate's rules were written while reading some public sets; libpostal was trained on OpenAddresses, which
  overlaps the National Address Database. A set that is "home" for any parser is reported but left out of every
  parser's aggregate.
- **Conflict of interest stated plainly:** doorplate's author builds the repository. The mitigations are blind
  labeling, a pre-registered score formula, a private twin of the golden set and the publication of every prediction
  file.
- **The sets are not a work list** for any parser: a rule change in a parser still needs a reason from another source.

## Schema and adapters

- The canonical schema is `schema/schema.toml`: coarse fields (house number, street, unit, PO box, route, city, state,
  postal code) with fine parts, and out-of-scope labels (recipient, building name, country) scored only where every
  parser claims them. The conventions list is `schema/conventions.toml` (see `schema/README.md`).
- Each parser is read through an adapter that returns character spans in its own labels, and a mapping file sends those
  labels to the schema. Mapping decisions are written at the top of each mapping file (for libpostal: `suburb` and
  `city_district` are city; `level`, `staircase` and `entrance` are units). A label a parser has and the schema does not
  is `other` and is never scored against it.
- Parsers run with default settings. libpostal is the Senzing model at a pinned commit and data checksum
  (`tools/libpostal/pins.env`).

## Sections to come
- How the golden set is labeled and adjudicated (`sets/golden/`).

## Difficulty tiers

Each golden record has a tier (`normal`, `hard`, `nightmare`) fixed by its shape class before any scored run; no parser's
output places a record in a tier. `normal` has a 100% ceiling, proved by checking that every gold label maps into all
three parsers' mapping files, not by running a parser. A public record's shape class is read from its gold fields
(blind labeling), a template's from the shape it was written from (`tools/golden/tiers.py`). `nightmare` shape classes come at most half from doorplate's own
rule research (the author's parser would otherwise be favored by construction) and at least half from outside it, and the
manifest states the split. Non-address and ambiguous records are reported apart and are not in the tier figures or the
Parser Score. Tiers are reported apart, never averaged by record count. The rules and sizes are in
`sets/golden/COMPOSITION.md`; the weights go in the Parser Score formula.

## How the golden set is sampled

About 1,500 records in six rounds of 250: 40% drawn at random from public-record sources and anonymized, 40% from hand
templates with invented values, 20% clean ordinary forms (`sets/golden/COMPOSITION.md`, fixed before any draw). Records
are picked by a seeded hash and the strata are fixed by shape and source, never by where parsers disagree. No parser is
run on a candidate. Every record is checked by string against doorplate's corpus, the benchmark suite, usaddress's
training files, libpostal's test sources and the geocode benchmark (`tools/golden/sample.py --check`). A private twin
with the same recipe and an unpublished seed is kept outside this repository to catch tuning to the public set.
## Scoring and the Parser Score

Fixed in `scorer/formula.toml` (issue #6) and merged before the first scored run; a later change is a PR that says why and
is listed in the report. Code: `scorer/` (see `scorer/README.md` for how to run it).

- **Record accuracy** (the headline): a record is right when every coarse field the gold has (house number, street, unit,
  PO box, route, city, state, postal code) is predicted with exactly the same character span and label, in any one of the
  gold's accepted readings (the conventions list and a card's `alternatives`). Text the gold leaves unlabeled is not
  scored; a predicted field the gold does not have costs precision (field F1), not record accuracy. Fine parts are folded
  into their coarse field first, so a parser that cannot split a street is not penalized on the headline.
- **Conventions are applied to every set and both sides alike** (`scorer/spans.py`): a lone letter after the house number
  is one answer whether read as a suffix or as the start of the street name; a `#` before a unit is never part of it.
- **Intervals:** 95% Wilson per part; the Parser Score and the field F1 score get a paired bootstrap (1,000 resamples,
  seed in the formula, records resampled within each part, the same draws for every parser).
- **Field F1:** micro-averaged precision and recall over the coarse fields of a part, plus a per-field table.
- **Fine track, reported apart:** record accuracy and F1 over the leaf labels (`street_name`, `unit_type`, ...), on records
  whose gold is fully fine-labeled. Every gold leaf counts for every parser, so a field a parser can only label whole
  (libpostal's `road`) is a miss on this track; it is not folded into any score. Adjacent words of one label join into one
  span, so the way a parser splits words does not count.
- **Parser Score** = 100 x the sum over scored parts of weight x coarse record accuracy. Weights: the golden set 0.50, shared
  equally by its three tiers (`normal`, `hard`, `nightmare`; flagged `non_address` and `ambiguous` records are reported
  on their own lines and are in no score); the other neutral parts share 0.50 equally: doorplate suite `natural` and
  `hand`, Senzing US `osm`, geocode `dev`. A parser's home sets (`usaddress-tests`, `libpostal-us`) and the parts drawn
  from a parser's failures (suite `hard`, Senzing `bug`) are reported apart and are in no score. The field F1 score is the
  same sum over micro F1. Speed and cost are never in the score (own table, step 8).
- **Sensitivity table:** the score under equal weights across parts, and with each set left out (weights renormalized),
  with the ranking, so a reader can see whether one set decides it.
- **Out-of-scope labels** (`recipient`, `building_name`, `country`) are scored only where every parser models them.
  Today none is: doorplate drops a trailing country on purpose and does not model building names (its
  `docs/usaddress-compat.md`, "Out of scope"), though its mapping file lists both. They are left out of every figure.
