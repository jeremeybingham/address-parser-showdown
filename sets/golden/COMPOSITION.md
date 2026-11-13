# Golden set: composition (fixed before any labeling)

> **Amended 2026-11-13 (labeling on the unmasked text):** the same cards (same seed, same draw, same ids; the redraw
> reproduced the committed rounds byte for byte) are now labeled on the row's own text, kept in the git-ignored
> `local-data/`, so a hard card can be checked on a map. The shipped text is then made from the labels (see
> "Anonymization"). Why: on the anonymized text the owner could not check a hard card, so its gold would be a guess. 13
> saves had been made; the 7 on public-record cards are labeled again.
>
> **Amended 2026-11-13 (issue #14):** difficulty tiers, added after labeling of round 1 began (15 saves; none of the
> sample, the draw or the seed changed). Rounds 1 to 6 below are unchanged; the new section "Difficulty tiers" is an
> addition, and rounds 7 and 8 hold the added `hard` and `nightmare` records. Why: the plan needs a tier with a 100%
> ceiling and two harder tiers, and redrawing would throw away labeling already done.
>
> **Amended 2026-11-13 (issue #26, round 9):** the rows the draw-time anonymizer filter dropped are restored as round 9
> (`tools/golden/sample.py --restore`). Rounds 1 to 6 and the walk that made them are unchanged (the redraw reproduces them
> byte for byte). Why: the filter dropped a candidate when doorplate's `Anonymizer` read the line differently after
> anonymizing (a parser run on a candidate, which the rules below forbid) or kept a word of four letters or more (most
> likely the rarer street types and unit words). Cards are labeled on the row's own text and `derive.py` makes the shipped
> text, so the filter is no longer needed, and each stratum becomes a plain random sample of its source after the stated
> duplicate and exclusion filters. The 219 rows the walk dropped (NAD 112, VA SCC 45, NY corps 28, FMCSA 16, TDLR 9, FCC
> amateur 9) are taken in the same hash order with the same style rule (own random generator; no anonymizer call on them);
> the duplicate and exclusion drops stay, which leaves 177 (`MANIFEST.md`). A restored row keeps the stratum and source of
> its walk and has `restored: true` in `provenance.jsonl`, so the report can show the public stratum with and without them.
> No text of round 9 ships until `derive.py` has made it from the labels; a card it holds back (a real word left outside a
> kept label) is counted in `MANIFEST.md`, so the remaining bias is visible. The anonymization rule below applies to rounds 1
> to 6 only.

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
- **Anonymization (draw):** house numbers, unit values and street names are replaced by invented ones with doorplate's
  `Anonymizer` (it keeps suffixes, directionals and unit words, so the shape survives); city, state and the five-digit ZIP
  are the real ones from the row. A record is dropped if the anonymizer changed how the line parses, or kept any word of
  four letters or more that is not a street type, directional or unit word. This text is `sets/golden/rounds/`; it fixes
  which records are in the set, and it is not what is labeled (amendment above).
- **Anonymization (shipped gold, `tools/golden/derive.py`):** labeling is done on the row's own text. For each labeled
  public-record card, the text inside the gold spans of house number, street name, unit, PO box and route values,
  recipient, building name and `other` is replaced by invented text of the same length and shape (digits by digits,
  words by invented words in the same case; street types, directionals, unit words and runs of one or two letters
  stay). The spans are the hand gold unchanged. A `non_address` card has its whole text replaced. A card is held back
  if a real word of four letters or more is left outside a type, direction, city, state or country label, or if the
  text matches an exclusion corpus after five tries. No parser is run in this step. A real typo inside a replaced value
  is not kept (a typo in a type, a city or the spacing is).
- **Exclusions:** a candidate whose text, or whose street line, matches (lowercase, letters and digits only) a string in any
  of these is dropped: doorplate's regression corpus and external test files, the benchmark suite v1, usaddress's training
  files, libpostal's test sources, the geocode benchmark. `tools/golden/sample.py --check` re-runs the check on the
  committed rounds and the shipped gold. libpostal's training data is not on disk and cannot be checked.
- **Sources are public records** (see each `NOTICE.md` in doorplate's `local-data/`); only invented or anonymized text ships; the row's own
  text stays in `local-data/`.

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
  (`military`, `urbanization`, `grid-utah`, `grid-wisconsin`, `spelled-number`, `intersection`, `highway-lettered`,
  `non-address-nightmare`, `box-glued`, `fraction-form`, `lot-trailer-site`). The record share of each side is fixed with the round 8 weights and stated in the manifest.

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
- **`nightmare` classes are paired (issue #22; survey in `docs/research/nightmare-survey.md`).** Every `nightmare` class
  has a `covered` variant (the form a closed rule or fixed report handles) and an `adjacent` variant (a nearby form an open
  issue leaves out), each with a `source` line in `CLASSES`. Why: doorplate's own rule research would otherwise make the
  tier a list of shapes doorplate was fixed for, so it would win by construction. The same pairing applies to the outside
  classes, using usaddress's and libpostal's closed and open issues. Rules:
  - Variants are defined by shape from the issue text. Doorplate is never run to confirm which variant fails, and a tag is
    never changed after a scored run. Every string is invented and passes the exclusion check.
  - The two variants of a class get equal numbers of records. With 18 classes and about 300 records that is about 8 per
    variant, so the report states the covered-versus-adjacent gap per parser at tier level only; per-class figures are
    descriptive.
  - No single parser's own tracker supplies more than a third of the outside `adjacent` records.
  - The doorplate-research side is 7 of 18 classes (about 39% of records, under the half cap); the manifest states the final
    shares (side, covered, adjacent) after the draw.
  - Adjacent records may be `ambiguous` or `doubtful`; they are reported apart as in the rules below.
  - `milepost` was dropped (no issue in any of the three trackers mentions it); `grid` is split into `grid-utah` and
    `grid-wisconsin`; `box-glued`, `fraction-form` and `lot-trailer-site` were added from the survey. `military` and
    `urbanization` keep a Pub 28 covered form and an open-issue adjacent form.
  - Round 7 (`hard`) is not paired: its classes are not derived from doorplate's rules.
  - Round 7 (`hard`, seed 20261114, `tools/golden/hard.py`): 299 records; the six added shape classes get 30 each, the
    non-addresses 20, and nine base `hard` classes 11 each. Sizes were fixed before the draw, by class only.
- **Typos (`hard` only)** are applied from observed typo classes (one-character slips, a dropped or doubled letter, glued
  words, a missing comma) onto invented values, never chosen by checking whether a parser fails.
- **Non-addresses and unparsable strings** carry a flag: `non_address` (gold: no fields) or `ambiguous` (more than one
  accepted reading, all listed). The owner decides which, per record, in labeling. They are reported on their own line and
  left out of the tier's accuracy figure and of the Parser Score, with their count shown.
- **Added rounds** use a new public seed (recorded here when drawn) and a private twin with an unpublished seed, the same
  recipe as rounds 1 to 6. Their records go through the same blind labeling and adjudication.
- **Reporting:** each tier on its own line with its interval and ceiling. Tiers are not averaged by record count; the
  Parser Score takes per-tier weights, fixed in the formula PR (#6) before the first scored run.
