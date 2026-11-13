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

## How the golden set is sampled

About 1,500 records in six rounds of 250: 40% drawn at random from public-record sources and anonymized, 40% from hand
templates with invented values, 20% clean ordinary forms (`sets/golden/COMPOSITION.md`, fixed before any draw). Records
are picked by a seeded hash and the strata are fixed by shape and source, never by where parsers disagree. No parser is
run on a candidate. Every record is checked by string against doorplate's corpus, the benchmark suite, usaddress's
training files, libpostal's test sources and the geocode benchmark (`tools/golden/sample.py --check`). A private twin
with the same recipe and an unpublished seed is kept outside this repository to catch tuning to the public set.
- The scoring and the Parser Score formula (`scorer/`), merged before the first scored run.
