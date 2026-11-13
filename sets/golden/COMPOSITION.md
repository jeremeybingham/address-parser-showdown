# Golden set: composition (fixed before any labeling)

> **Amended 2026-11-13 (issue #14):** difficulty tiers, added after labeling of round 1 began (15 saves; none of the
> sample, the draw or the seed changed). Rounds 1 to 6 below are unchanged; the new section "Difficulty tiers" is an
> addition, and rounds 7 and 8 hold the added `hard` and `nightmare` records. Why: the plan needs a tier with a 100%
> ceiling and two harder tiers, and redrawing would throw away labeling already done.

Step 2 of the plan (issue #3). This page and `tools/golden/sample.py` are committed before any record is drawn or
labeled. A later change is a PR that says why and is listed in the report.

## Size and rounds

About 1,500 records (enough for 95% intervals of about plus or minus one point), labeled in six rounds of 250. Each round
has the same mix (a stratum is shuffled with the seed and dealt evenly), so a stopped labeling run is still a fair sample.

## Strata

| Stratum | Share | Records | How |
|---|---|---|---|
| `public` | 40% | 600 | Drawn at random from public-record sources, then anonymized. NAD 300; five messy sources 60 each: FMCSA Company Census, Texas TDLR licenses, Virginia SCC business registry, NY active corporations, FCC amateur licenses |
| `template` | 40% | 600 | Written from hand templates of real shapes with invented values (`tools/golden/templates.py`) |
| `clean` | 20% | 300 | Ordinary forms: NAD addresses with a plain number, a plain street and no unit, in the form `street, city, ST ZIP` |

Shapes in the templates (weights in `templates.py`): street with unit, PO box in nine spellings, rural route, highway
and county road, directionals (pre and post), fractions, number with a letter, hyphenated and grid numbers, care-of,
general delivery, plain street. Modifiers: none, one-character typo, UPPER, lower, no commas, no ZIP, no state.

## Rules

- **Sampling is by seeded hash, never by parser behavior.** Each source is sorted by `hash(row, seed)`; the first rows that
  pass the filters are kept. No parser is run on a candidate. (A disagreement-driven pick is what made the benchmark
  suite's `hard` stratum unfair to a third parser.)
- **Public seed: 20261112.** The private twin uses an unpublished seed with the same recipe.
- **Anonymization:** house numbers, unit values and street names are replaced by invented ones with doorplate's
  `Anonymizer` (it keeps suffixes, directionals and unit words, so the shape survives); city, state and the five-digit ZIP
  are the real ones from the row. A record is dropped if the anonymizer changed how the line parses, or kept any word of
  four letters or more that is not a street type, directional or unit word.
- **Exclusions:** a candidate whose text, or whose street line, matches (lowercase, letters and digits only) a string in any
  of these is dropped: doorplate's regression corpus and external test files, the benchmark suite v1, usaddress's training
  files, libpostal's test sources, the geocode benchmark. `tools/golden/sample.py --check` re-runs the check on the
  committed rounds. libpostal's training data is not on disk and cannot be checked.
- **Sources are public records** (see each `NOTICE.md` in doorplate's `local-data/`); only anonymized text ships.

## Difficulty tiers (added 2026-11-13, issue #14)

Every record also has a **tier**. Tier is independent of the strata above (source); a record has one of each. Tiers are
fixed by the record's shape class by a script, before any scored run, and never by how a parser did on it.

| Tier | Holds | Ceiling | Records (suggested) |
|---|---|---|---|
| `normal` | Gold-verified (blind labeling plus adjudication) records whose gold uses only the coarse fields and the accepted readings in `schema/conventions.toml`, and whose every gold label has a target in all three mapping files. No typos, no non-addresses | 100% | about 1,100 of rounds 1 to 6 |
| `hard` | Rarer shapes and real-world typos, a few non-addresses, strings that strain the limits of a parser | below 100% | about 400 of rounds 1 to 6, plus about 300 new (round 7) |
| `nightmare` | Mostly the rarest and most difficult shapes, including known-unparsable examples | well below 100% | about 300 new (round 8) |

Each tier has at least about 300 records (95% interval about plus or minus five points).

### Shape classes and the tagger (added 2026-11-13)

The class-to-tier table is `CLASSES` in `tools/golden/tiers.py`, committed before rounds 7 and 8 are drawn. In short:

- `normal`: `street-plain`, `ordinary`, `street-unit`, `directional`, `number-letter`, `po-box`, `highway`.
- `hard`: `fraction`, `hyphen-number`, `rural-route`, `care-of`, `general-delivery`, `typo`, `box-and-street`,
  `named-place`, `no-street`; added in round 7: `typo-glued`, `typo-type`, `zip4-plain`, `state-spelled`, `two-units`,
  `pre-type`, `non-address-hard`.
- `nightmare` (round 8): 7 classes from doorplate's rule research (`second-number`, `letter-before-street`,
  `no-so-direction`, `county-road-compass`, `zip4-cut`, `unit-before-street`, `paren-unit`) and 8 from outside it
  (`military`, `urbanization`, `grid`, `spelled-number`, `intersection`, `highway-lettered`, `milepost`,
  `non-address-nightmare`). The record share of each side is fixed with the round 8 weights and stated in the manifest.

A template record's class is the shape it was written from; the typo modifier makes it `typo`. A public or clean record
has no written shape, so its class is read from its **gold** fields (`class_from_gold`: a route, a box, a box with a
street, a name the schema scores for nobody, two units, a number prefix or suffix, a unit, a directional, else plain).
Gold is blind labeling, so no parser output enters. Then the `normal` check: the gold uses core fields only, each one is
in all three mapping files, the card is not `doubtful` and has no flag; otherwise the record moves up to `hard`.
Measured from provenance alone, the 600 template records of rounds 1 to 6 split 431 `normal` and 169 `hard` before the
check.

### Rules

- **The shape-class table is committed before the added rounds are drawn** (`tools/golden/tiers.py`): each class names its
  tier. A record whose class says `normal` but fails the mapping check (a gold label with no target in some parser's
  mapping) moves up to `hard`; it is not dropped.
- **No parser output places a record in a tier.** The `hard` rule of the benchmark suite (drawn from two parsers' blind
  spots) is the counter-example.
- **`nightmare` is not a doorplate rule list.** Shape classes come from two places, and the manifest states the share:
  at most half from doorplate's 0.5.x and 0.6.x rule research (the shape class only; every string is freshly invented and
  must pass the exclusion check against doorplate's corpus and changelog examples), and at least half from outside it:
  usaddress's and libpostal's own failure modes (issues and docs), USPS Publication 28 odd forms, and the geocode
  benchmark's error types.
- **Typos (`hard` only)** are applied from observed typo classes (one-character slips, a dropped or doubled letter, glued
  words, a missing comma) onto invented values, never chosen by checking whether a parser fails.
- **Non-addresses and unparsable strings** carry a flag: `non_address` (gold: no fields) or `ambiguous` (more than one
  accepted reading, all listed). The owner decides which, per record, in labeling. They are reported on their own line and
  left out of the tier's accuracy figure and of the Parser Score, with their count shown.
- **Added rounds** use a new public seed (recorded here when drawn) and a private twin with an unpublished seed, the same
  recipe as rounds 1 to 6. Their records go through the same blind labeling and adjudication.
- **Reporting:** each tier on its own line with its interval and ceiling. Tiers are not averaged by record count; the
  Parser Score takes per-tier weights, fixed in the formula PR (#6) before the first scored run.
