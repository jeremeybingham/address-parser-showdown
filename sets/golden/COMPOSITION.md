# Golden set: composition (fixed before any labeling)

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
