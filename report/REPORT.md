# US address parsers on equal terms: doorplate, usaddress and libpostal

Report for v0.1.0 of `address-parser-showdown`, written from the pinned run [`runs/2026-11-16/`](../runs/2026-11-16/)
(commit `4ef4064`, 2026-11-15). Every figure below comes from that run's committed prediction files unless it says
otherwise, and can be reproduced from them (`just rescore runs/2026-11-16`). The figures in sections 7.4 and 7.5 come
from `tools/report/breakdown.py`, which scores the same committed predictions.

**Conflict of interest.** doorplate's author built this repository, labeled the golden set and wrote this report.
Section 10 lists what was done about that and what it does not cover.

## 1. Abstract

Three US address parsers were compared on equal terms: doorplate 0.6.0 (rules), usaddress 0.5.16 (a conditional random
field) and libpostal with Senzing's 1.2.0 model (an averaged-perceptron CRF trained on OpenStreetMap and
OpenAddresses). All three are read through adapters into one neutral label schema and scored on character spans. The
sets are a new hand-labeled golden set of 2,439 records in three difficulty tiers, four outside sets used as neutral
parts, and each parser's home test files, which are reported apart. The headline is the pre-registered Parser Score
(formula version 1, fixed before the first run): coarse record accuracy, half on the golden set's three tiers and half
on the neutral parts. doorplate scores 90.9 (95% bootstrap interval 89.8 to 92.0), usaddress 84.7 (83.4 to 86.0) and
libpostal 80.8 (79.5 to 82.2). The ranking holds in every sensitivity row, including with each set left out.

On the golden set's random public stratum alone (829 records drawn at random from public records), the three are
close: 93.7, 93.0 and 91.3 for doorplate, usaddress and libpostal. On that stratum, doorplate against usaddress is not
a significant difference (exact McNemar p = 0.31), while doorplate against libpostal (p = 0.001) and usaddress against
libpostal (p = 0.04) are. Most of the spread in the Parser Score comes from rarer shapes: rural routes, military
lines, units in unusual places and typos. Two changes were made after the first run; both are in section 6 and
neither changes the ranking. doorplate is about five times faster than libpostal and eight times faster than usaddress
in one process, and libpostal needs about 3 GB of memory and disk where the other two need under 30 MB.

## 2. Parsers and versions

| Parser | Version and pins | Method | Labels |
|---|---|---|---|
| doorplate | 0.6.0 | Hand-written rules in Rust, with Python bindings | usaddress's label names (fine) |
| usaddress | 0.5.16, python-crfsuite 0.9.12, default model | Linear-chain CRF (Lafferty et al. 2001) through python-crfsuite | fine (pre-type, pre-modifier, ...) |
| libpostal | commit `25099c50`, Senzing model (parser 1.2.0), data checksum `a42c356d…`, pypostal 1.1.11 | CRF trained with averaged perceptron on OpenStreetMap and OpenAddresses | coarse (`road`, `house_number`, `unit`, ...) |

Each parser runs with its default settings; nothing was retrained or tuned. The libpostal pins are in
`tools/libpostal/pins.env`, and `tools/libpostal/build.sh --verify` checks a build against them. `run.json` in the run
folder records the versions, every set's SHA-256 and the machine.

## 3. Related work

- **usaddress** (DataMade) parses US addresses with a linear-chain conditional random field (Lafferty et al. 2001)
  trained through python-crfsuite. Its repository ships labeled training data and regression tests. This report treats
  those tests as usaddress's home set (section 5).
- **libpostal** (Barrentine; openvenues) parses addresses worldwide with a model trained on OpenStreetMap and
  OpenAddresses (Barrentine 2017). Senzing publishes a retrained model (`libpostal-data`, used here) and a
  multi-country test file. That file's US rows are a neutral part here, apart from the rows reported as libpostal bugs.
- **The geocoding address-parsing benchmark** (Yin, Li and Goldberg 2023) holds about 239,000 US address strings with
  input errors mined from a geocoder's logs, tagged IOB. Its `dev` split is a neutral part here. Its `test` split is
  left out, because doorplate's rules were written while reading it.
- **MessyStreets** (Gaere 2026) is a benchmark for geocoding real addresses taken from the web. It is cited only. It is
  not used here: its terms are for research use, and it scores geocoders rather than parsers.
- **Standards.** USPS Publication 28 defines the postal address line and its abbreviations. The FGDC address standard
  (FGDC-STD-016-2011) defines address elements for data exchange. The National Address Database (USDOT) is the source of most public golden rows and of doorplate's suite.

Each project's own published figures come from its own tests, which is why the home sets are reported apart here.

## 4. The schema and the conventions

The schema (`schema/schema.toml`) has eight core coarse fields: `house_number`, `street`, `unit`, `po_box`, `route`,
`city`, `state` and `postal_code`. It also has out-of-scope fields (`recipient`, `building_name`, `country`) and
`other`. Each coarse field has fine parts: for example `street_pre_direction`, `street_pre_type`, `street_name`,
`street_post_type` and `street_post_direction` for a street. A mapping file per parser sends its labels to the schema
(`adapters/mappings/`). A label the schema does not hold maps to `other` and is never scored. No out-of-scope field is
scored, because no parser claims all three (doorplate drops a trailing country on purpose).

Two **conventions** were fixed by the owner before the first run (`schema/conventions.toml`). Each one accepts more
than one reading for every set and every parser:

1. **A letter after the house number** (`214 B Elm St`): the letter may be read as the number's suffix or as the start
   of the street name.
2. **A `#` before a unit** (`Apt #4`, `# 4`): the `#` may be part of the unit or left unlabeled.

Two other candidates were considered and left to the gold: `EXT` after a street, and a compass word that starts a city
(`S Elgin`). A card can also carry its own accepted readings (`alternatives`). An example is a street that could also
be read as a route; section 6 covers the 140 highway cards that got one after the first run.

## 5. The sets

| Set | Parts scored | Records | Role |
|---|---|---|---|
| golden (this repository) | `normal`, `hard`, `nightmare` | 1,568 + 556 + 226 in the tiers (2,439 shipped) | 0.50 of the Parser Score, split equally over the tiers |
| doorplate suite v1 | `natural`, `hand` | 16,001 + 1,000 | neutral; built by doorplate's author (section 10) |
| Senzing test data, US rows | `osm` | 2,172 | neutral |
| geocode benchmark | `dev` | 60,522 | neutral |
| doorplate suite v1 | `hard` | 2,585 | reported apart: drawn from the blind spots of two of the three parsers |
| Senzing test data, US rows | `bug` | 6 | reported apart: cases reported as libpostal bugs |
| usaddress tests | six files | 9,088 | reported apart: usaddress's home set |
| libpostal `test_us_parses` | `us` | 53 | reported apart: libpostal's home set |

The four neutral parts share the other 0.50 equally. Each set's source, license, counts and checksums are in its
`sets/*/MANIFEST.md`. Sets without a license to ship are read from a local copy or downloaded by script, and checked
by SHA-256.

## 6. The golden set: how it was made and labeled

### 6.1 Sampling

The golden set holds 2,439 shipped records from twelve rounds (`sets/golden/COMPOSITION.md`, `MANIFEST.md`). Every
rule was written before its round was drawn.

| Rounds | Drawn from | Shipped |
|---|---|---|
| 1 to 6 and 11 | 40% public records (NAD, FCC amateur licenses, FMCSA, NY corporations, TDLR, Virginia SCC), drawn by a seeded walk; 40% hand templates with invented values; 20% clean ordinary forms | 1,497 |
| 7 (`hard`) | invented strings of rare and typo shapes | 270 |
| 8 (`nightmare`) | invented strings of the hardest shapes, in pairs of a `covered` form (one a closed rule or a fixed report handles) and an `adjacent` form (a nearby form an open issue leaves out) | 230 |
| 9 | the public rows the anonymizer filter had dropped from rounds 1 to 6, restored so that no filter depends on how a parser reads a row | 163 |
| 10 | SBA PPP loan addresses, as the borrower wrote them | 249 |
| 12 | real Utah and Wisconsin grid addresses and military lines, pre-labeled from the source fields | 30 |

No parser was run on any candidate. Every record was checked by string against doorplate's corpus and suite,
usaddress's training files, libpostal's test sources and the geocode benchmark. libpostal's training data was not on
disk and could not be checked.

The tiers are fixed by a **shape class** read from the gold, or from the template shape the record was written from
(`tools/golden/tiers.py`), never from a parser's output. A `normal` record uses only core fields, and every gold label
in it has a target in all three mapping files, so the tier's ceiling is 100%. 87 records move up to `hard` by that
check, 64 of them highway cards (their gold uses `route`, and libpostal has no route label).

`nightmare` classes come at most half from doorplate's own rule research: of the 264 records drawn, 126 (48%) came from
it and 138 (52%) from outside it.

### 6.2 Labeling

There was one labeler, the owner, labeling blind. Spans were dragged on a local page that shows only the text: no
pre-labels and no parser output (`tools/label/README.md`). Public rows were labeled on their real text, which is kept
private. The shipped text is made from the labels by replacing private values with invented ones of the same length
(`tools/golden/derive.py`), so the shipped spans are the hand gold unchanged.

Each card records two things. The first is what the text is: one door, `multi_address`, `intersection`, `ambiguous` or
`non_address`. The second is how sure the labeler is: sure, `doubtful` or `rough`. Only one-door, sure records count
in a tier's figure. The others are reported on their own lines: 55 records from `hard` (9.0%) and 34 from `nightmare`
(13.1%), both under the 15% warning line. 69 cards were removed (`removed.jsonl`): 35 invented cards of rounds 7 and 8 that could
not be checked or defended, and 34 more the owner marked to remove (27 non-addresses, 1 grid number, 6 others). Their
ids are not reused.

### 6.3 Adjudication, and which way it moved the gold

Adjudication came after every round was labeled. Each parser was run once, and every span a parser read that the gold
does not hold was listed. The page showed these readings without the parser's name, and the owner decided card by
card. `tools/label/direction.py` measures the result. For each card it compares the gold before adjudication (the last
blind save) with the gold after, and counts the parser readings that were questions before and not after (a move
*toward* that parser) or the reverse (*away*). Words of one label are joined first on both sides, so saving `New York`
as one city span instead of two does not count as a change.

| | doorplate | usaddress | libpostal |
|---|---|---|---|
| Cards moved toward the parser's reading | 20 | 20 | 2 |
| Cards moved away from it | 1 | 2 | 1 |
| Spans toward / away | 36 / 2 | 37 / 4 | 2 / 1 |

Of 1,264 adjudicated cards, the reading changed on 22. The columns are not exclusive: doorplate and usaddress share
label names, so one change can move toward both. Another 514 cards changed only in format (a multi-word city
saved as one span), which is not a reading change. There is no second labeler, so no agreement statistic between
labelers (kappa or similar) exists. The figures above are the only check on the adjudication.

**Marks changed after parser output was seen.** 13 cards changed a mark during or after adjudication (`late_changes`).
11 of them left the tier figures: 10 became `doubtful` and 1 `non_address`. 1 went from doubtful back to sure, and 1
gained a region that is not scored. On those 11 cards, doorplate reads 3 right, usaddress 4 and libpostal 4, so no
parser lost or gained a share by the move. The sensitivity row "with the doubtful records" puts them back.

### 6.4 Changes after the first run

The first pinned run is [`runs/2026-11-15/`](../runs/2026-11-15/), kept unchanged (to rescore it, check out its
commit, `18ee6b2`: today's scorer and gold give the 2026-11-16 figures). Reading its counts of records no
parser reads right turned up two faults. The owner chose to fix both and to make a new pinned run, rather than correct
figures by hand.

1. **Scorer fault** (commit `d6fddf5`). An accepted alternative that covers more than one gold span was added beside
   those spans instead of replacing them, so it could never match. It now replaces every gold span it overlaps, and a
   regression test covers it. This touches only cards with such an alternative (such as the 30 highway cards that
   already had a street alternative by hand).
2. **Highway cards** (commit `87217c2`). 140 cards label a numbered highway (`US Hwy 74`, `State Route 9`, `County
   Road 12`) as `route_type` and `route_value`. The schema reads a highway as a street, and keeps `route` for rural,
   highway contract and military routes. The owner kept the route reading and added the schema's as an accepted
   alternative: one `street_name` span over the run of route spans. A rule over the gold made the change
   (`tools/golden/highway_alt.py`; no parser is run). By round: 7, 15, 23, 14, 13, 14, 4, 27, 3, 13, 7 and 0 cards.
   Spans, marks and tiers are unchanged.

The Parser Score formula and the conventions list were not changed.

| Figure | run 2026-11-15 | scorer fix only (not committed) | run 2026-11-16 |
|---|---|---|---|
| Parser Score, doorplate / usaddress / libpostal | 86.0 / 80.2 / 76.0 | 86.9 / 81.1 / 76.8 | 90.9 / 84.7 / 80.8 |
| golden `hard`, same order | 68.3 / 66.5 / 48.7 | 73.2 / 71.6 / 53.6 | 91.2 / 88.5 / 70.9 |
| golden `nightmare`, same order | 62.4 / 46.0 / 46.9 | 63.3 / 46.5 / 47.3 | 69.0 / 51.3 / 54.0 |
| golden `normal`, same order | 95.0 / 93.6 / 91.8 | unchanged | 95.0 / 93.6 / 91.8 |

Every prediction file of the two runs is byte-identical; only the scoring changed. The large rise in `hard` comes from
the highway cards: before the change, no parser could read them right, because they read a highway as a street. That
these went unseen until the run is a weakness of a single labeler (section 10).

## 7. Scoring and results

### 7.1 How a record is scored

A record is **right** when every coarse field the gold has is predicted with exactly the same character span and the
same label, in any one of the gold's accepted readings (the conventions plus the card's alternatives). Fine parts are
folded into their coarse field, and neighbouring spans of one field are joined first. This means a parser that labels
a street only as a whole (libpostal's `road`) is not penalized on the headline. Text the gold leaves unlabeled is not
scored. A field predicted where the gold has none costs field F1, but not record accuracy. Intervals are 95% Wilson
(Wilson 1927) per part. The Parser Score and the field F1 score get a paired bootstrap (Efron 1979): 1,000 resamples
with seed 20261113, records resampled within each part, and the same draws for every parser.

**Parser Score** = 100 × Σ over scored parts of weight × coarse record accuracy. The weights (`scorer/formula.toml`,
version 1) are 0.50 for the golden set (one sixth per tier) and 0.50 for the four neutral parts (one eighth each). The
field F1 score is the same sum over micro field F1.

### 7.2 Parser Score

| Parser | Parser Score (95% interval) | Field F1 score (95% interval) |
|---|---|---|
| doorplate | **90.9** (89.8 to 92.0) | 97.6 (97.3 to 97.9) |
| usaddress | **84.7** (83.4 to 86.0) | 95.7 (95.3 to 96.1) |
| libpostal | **80.8** (79.5 to 82.2) | 93.4 (92.8 to 93.9) |

| Sensitivity | doorplate | usaddress | libpostal | Ranking |
|---|---|---|---|---|
| formula weights | 90.9 | 84.7 | 80.8 | doorplate > usaddress > libpostal |
| equal weights over parts | 91.7 | 85.7 | 82.1 | same |
| doubtful records put back | 90.4 | 84.3 | 80.6 | same |
| without doorplate suite | 88.8 | 81.7 | 77.9 | same |
| without geocode `dev` | 90.4 | 84.2 | 80.9 | same |
| without golden | 96.7 | 91.6 | 89.4 | same |
| without Senzing `osm` | 89.9 | 83.9 | 78.2 | same |

### 7.3 Per part

Coarse record accuracy, 95% Wilson interval:

| Set / part | Records | No parser right | doorplate | usaddress | libpostal |
|---|---|---|---|---|---|
| golden / normal | 1,568 | 64 | 95.0 (93.8 to 95.9) | 93.6 (92.2 to 94.7) | 91.8 (90.3 to 93.0) |
| golden / hard | 556 | 27 | 91.2 (88.5 to 93.3) | 88.5 (85.6 to 90.9) | 70.9 (67.0 to 74.5) |
| golden / nightmare | 226 | 34 | 69.0 (62.7 to 74.7) | 51.3 (44.8 to 57.8) | 54.0 (47.5 to 60.4) |
| doorplate suite / natural | 16,001 | 53 | 98.6 (98.4 to 98.8) | 96.5 (96.2 to 96.7) | 95.0 (94.6 to 95.3) |
| doorplate suite / hand | 1,000 | 15 | 95.8 (94.4 to 96.9) | 91.1 (89.2 to 92.7) | 84.0 (81.6 to 86.1) |
| Senzing US / osm | 2,172 | 6 | 98.1 (97.4 to 98.6) | 90.6 (89.3 to 91.7) | 98.8 (98.3 to 99.2) |
| geocode / dev | 60,522 | 830 | 94.4 (94.2 to 94.6) | 88.4 (88.1 to 88.6) | 79.9 (79.6 to 80.2) |
| *Reported apart* | | | | | |
| doorplate suite / hard | 2,585 | 145 | 73.4 | 25.7 | 69.0 |
| Senzing US / bug | 6 | 0 | 100.0 | 83.3 | 100.0 |
| usaddress tests / labeled | 146 | 0 | 81.5 | 100.0 | 68.5 (1 error) |
| usaddress tests / us50_test_tagged | 687 | 0 | 96.8 | 100.0 | 95.3 |
| usaddress tests / synthetic (two files) | 8,242 | 6 | 99.8 to 99.9 | 99.8 to 100.0 | 99.8 to 99.9 |
| libpostal / test_us_parses | 53 | 2 | 84.9 | 88.7 | 94.3 |

Each parser leads on its own home set, as expected. Every row with intervals, the held-out records and the fine track
are in [`runs/2026-11-16/results.md`](../runs/2026-11-16/results.md).

### 7.4 Per field (golden set, micro F1)

| Tier | Field | doorplate | usaddress | libpostal |
|---|---|---|---|---|
| normal | street | 98.4 | 97.8 | 94.9 |
| normal | unit | 84.8 | 81.9 | 80.0 |
| normal | house number / city / state / ZIP | 98.7 to 100.0 | 98.6 to 100.0 | 97.4 to 99.9 |
| hard | street | 92.5 | 92.3 | 78.4 |
| hard | unit | 88.8 | 87.9 | 61.3 |
| hard | PO box | 92.3 | 81.1 | 45.7 |
| hard | route | 94.0 | 93.5 | 0.0 |
| nightmare | street | 84.9 | 72.1 | 69.5 |
| nightmare | unit | 65.6 | 41.2 | 64.5 |
| nightmare | PO box | 80.0 | 30.3 | 17.1 |
| nightmare | route | 60.0 | 19.5 | 0.0 |

libpostal has no route label, so every route in the gold is a miss for it. A route is 0.0 F1 by construction, not a
fault of the model. The fine track (every leaf label counts) is reported apart and in no score. doorplate gets 94.4 on
`normal`, usaddress 93.0 and libpostal 0.0, because libpostal does not split a street or a house number.

### 7.5 The golden set by stratum

The issue #26 review proposed the random public stratum as a headline, since it is the part of the golden set closest
to a random sample of real US address lines. It is reported here beside the Parser Score. It is not in the formula.

| Group | Records | doorplate | usaddress | libpostal |
|---|---|---|---|---|
| **Public, random walk (rounds 1 to 6 and 11)** | 829 | 93.7 (91.9 to 95.2) | 93.0 (91.1 to 94.5) | 91.3 (89.2 to 93.0) |
| Public, restored rows (round 9) | 107 | 89.7 (82.5 to 94.2) | 87.9 (80.3 to 92.8) | 86.0 (78.2 to 91.3) |
| SBA PPP, as written (round 10) | 245 | 97.1 (94.2 to 98.6) | 98.8 (96.5 to 99.6) | 95.5 (92.1 to 97.5) |
| Clean ordinary forms | 346 | 99.1 (97.5 to 99.7) | 99.1 (97.5 to 99.7) | 97.7 (95.5 to 98.8) |
| Templates, all tiers | 1,038 | 87.6 (85.4 to 89.4) | 81.4 (78.9 to 83.7) | 72.3 (69.5 to 74.9) |
| Real grid and military lines (round 12) | 30 | 90.0 (74.4 to 96.5) | 73.3 (55.6 to 85.8) | 60.0 (42.3 to 75.4) |

Paired differences (exact McNemar test on the records one parser reads right and the other wrong):

| Pair | Random public stratum: A only / B only, p | Whole golden set: A only / B only, p |
|---|---|---|
| doorplate vs usaddress | 15 / 9, p = 0.31 | 120 / 43, p < 0.001 |
| doorplate vs libpostal | 26 / 6, p = 0.001 | 238 / 41, p < 0.001 |
| usaddress vs libpostal | 27 / 13, p = 0.04 | 209 / 89, p < 0.001 |

On ordinary public address lines, the three parsers are within 2.5 points of each other, and doorplate and usaddress
cannot be told apart at this size. The Parser Score's spread comes from the templates and the outside sets, which are
weighted toward shapes that are rare in a random draw. A reader whose data is mostly ordinary street lines should weigh
the random stratum. A reader whose data has rural routes, military mail, units in odd places or typos should weigh the
tiers.

**Real text against invented text.** The shipped golden text replaces private values with invented ones. Scoring the
same 1,312 public cards on their real (private) text gives doorplate 95.8, usaddress 93.7 and libpostal 92.8. On the
shipped text the same cards give 94.7, 93.8 and 91.8. The invented values cost each parser at most about one point,
and they do not change the ordering. So the concern that invented names hurt the statistical parsers more is not
supported here.

## 8. Speed and cost

These figures are never part of the Parser Score. They come from 100,000 strings (the shipped golden set's 2,439
strings, repeated), the median of 5 passes, on an Intel i9-9900K under WSL2 with 4 CPUs used. Each parser's own call
is timed, without the adapter.

| | doorplate | usaddress | libpostal |
|---|---|---|---|
| Strings per second, one process | 72,028 | 8,952 | 14,577 |
| Strings per second, 4 processes | 223,510 | 28,054 | 43,951 |
| Load time (import and first parse) | 0.003 s | 0.012 s | 3.480 s |
| Memory after loading, one process | 27 MB | 27 MB | 2,958 MB |
| Memory, 4 processes together | 37 MB | 42 MB | 11,771 MB |
| Install size | 4.9 MB | 4.8 MB | 2,993.1 MB |

Speed varies between runs on this machine by 5 to 14%: run 2026-11-15 measured 64,876, 8,395 and 12,818 strings per
second in one process. The reference profile (4 CPUs, 8 GB) is not enforced. Four libpostal processes need 11.8 GB, so
libpostal cannot run four-wide inside that profile.

## 9. Error analysis by shape

The tables in this section give coarse record accuracy per shape class over all tiers
(`python -m tools.report.breakdown runs/2026-11-16`). Every example string is invented for this report.

**Where all three do well.** All three score 97% or more on plain streets (588 records), ordinary forms (249),
directionals (331), PO boxes (92) and spelled-out states (30).

**Where they differ.** The example column shows the kind of string in each class; it is not a card from the set.

| Shape class | Records | doorplate | usaddress | libpostal | Example (invented) |
|---|---|---|---|---|---|
| rural-route | 108 | 97.2 | 92.6 | 40.7 | `RR 3 Box 41, Zeller, MO 65000` |
| military | 24 | 62.5 | 16.7 | 0.0 | `PSC 4021 Box 77, APO AE 09001` |
| two-units | 30 | 100.0 | 100.0 | 50.0 | `9 Elm St Bldg 2 Apt 5` |
| hyphen-number | 24 | 100.0 | 100.0 | 62.5 | `12-40 Ash Ave` |
| fraction | 35 | 100.0 | 71.4 | 85.7 | `18 1/2 Pine St` |
| spelled-number | 12 | 75.0 | 41.7 | 8.3 | `Four Mill Rd` |
| letter-before-street | 16 | 81.2 | 37.5 | 50.0 | `410 W B St` |
| county-road-compass | 14 | 64.3 | 28.6 | 78.6 | `County Road 6 N` |
| unit-before-street | 15 | 80.0 | 40.0 | 53.3 | `Apt 3, 15 Oak Ct` |
| paren-unit | 17 | 17.6 | 17.6 | 52.9 | `22 Birch Ln (Unit 4)` |
| lot-trailer-site | 19 | 52.6 | 52.6 | 73.7 | `600 Hill Rd Lot 31` |
| named-place | 31 | 74.2 | 90.3 | 90.3 | `Harbor Plaza, 5 Dock St` |
| typo-type | 30 | 63.3 | 83.3 | 56.7 | `77 Maple Stret` |
| zip4-cut | 18 | 50.0 | 66.7 | 55.6 | `Zeller, MO 65000-12` |

**Where all three fail.**

| Shape class | Records | doorplate | usaddress | libpostal | Example (invented) |
|---|---|---|---|---|---|
| number-letter (in `normal`) | 26 | 26.9 | 15.4 | 11.5 | `31B Cedar St` |
| typo-glued | 30 | 43.3 | 43.3 | 43.3 | `8 OakSt Zeller,MO 65000` |
| box-glued | 9 | 44.4 | 33.3 | 22.2 | `POBox12` |
| fraction-form | 16 | 62.5 | 37.5 | 18.8 | `5½ Oak St` |

Two readings of these tables:

- **libpostal's** losses are mostly shapes its labels or training do not hold well: routes (no label), military
  lines, a second unit, hyphenated numbers and spelled-out numbers. It does better than the other two on units in
  parentheses, lots and trailer sites and county roads with a compass word, and as well as usaddress on named places.
- **usaddress and doorplate** share label names and read most ordinary and `hard` shapes alike. They part on the
  `nightmare` forms, where doorplate's rules cover more: military lines, letter streets, units before the street and
  spelled numbers. doorplate's rules were written near some of these forms, so see section 10.

**An open question about the `number-letter` class.** In 19 of the 26 cards doorplate misses, the gold reads a letter
joined to the number (`31B`) as the unit (`unit_value`). All three parsers read it as part of the house number, and
the letter-after-number convention covers only a letter written apart, read as a suffix or a street name. This is a
gold reading that no parser makes. It may be right (Publication 28 allows a unit written that way) or a labeling
habit. It is not changed after the run. It is listed here and in the owner's open items, so that a later version can
decide it, with a convention or not, before its run.

**The covered and adjacent pairs in `nightmare`.** A `covered` form is one that a closed rule or a fixed bug report
handles. An `adjacent` form is a nearby form that an open issue leaves out.

| Variant | Records | doorplate | usaddress | libpostal |
|---|---|---|---|---|
| covered | 109 | 77.1 | 49.5 | 56.0 |
| adjacent | 117 | 61.5 | 53.0 | 52.1 |

doorplate drops 15.6 points from the covered forms to the adjacent ones. usaddress rises 3.5 and libpostal drops 3.9.
That is the pattern to expect if doorplate's lead on `nightmare` comes partly from rules written for the exact forms
drawn. On the adjacent forms alone, doorplate still leads by 8.5 points, but the intervals of the three overlap
(52.5 to 69.9 against 44.0 to 61.8 and 43.2 to 61.0).

## 10. Threats to validity

- **Author conflict.** doorplate's author built the repository, chose the schema and the formula, labeled the golden
  set and wrote this report. The mitigations: labeling was blind; the formula and the conventions were fixed in a PR
  before the first run and not changed after; every prediction file is committed; the adjudication direction is
  published (section 6.3); and `nightmare` classes from doorplate's own research are capped at half. What the
  mitigations do not cover: the author's sense of what an address looks like shaped the templates, the shape classes
  and the gold readings. The doorplate suite was built by the same author, and its two parts carry half of the neutral weight
  (a quarter of the score); leaving it out keeps the ranking (88.8 / 81.7 / 77.9).
- **The twin's gap is not measured.** A private twin of the golden set (the same recipe with an unpublished seed) was
  drawn to catch tuning to the public draw. It has not been labeled, so v0.1.0 has no twin figure. Until it is
  labeled, nothing here shows that doorplate's golden figures would hold on a fresh draw.
- **Training and rule overlap.** libpostal was trained on OpenAddresses, which overlaps the National Address
  Database. Most public golden rows and the doorplate suite's `natural` part come from NAD, so libpostal may have seen
  near copies. doorplate's rules were written while reading public sets, including the geocode benchmark's `test`
  split (left out here) and doorplate's own corpus (checked by string, no matches kept). usaddress's training files
  were checked by string against the golden set, but its training shapes may still be close to the templates.
  libpostal's training data could not be checked.
- **US only.** Every set is US addresses in English. libpostal is built for worldwide addresses, and nothing here says
  how it compares outside the US.
- **A single labeler.** No second person labeled any card, so there is no agreement figure between labelers. The 140
  highway cards (section 6.4) show the risk: a consistent habit against the schema went unseen until the run. Other
  habits may remain; one candidate is the `number-letter` reading in section 9.
- **Changes after the first run.** Both changes in section 6.4 were found by reading the first run's results, so they
  were made with the parsers' scores in view. Neither touches the formula or the conventions. The first run is kept
  unchanged for comparison, and the ranking is the same in both runs.
- **Mapping choices.** Each parser's labels reach the schema through a mapping file. Some choices are judgement calls,
  stated at the top of each file. For example, libpostal's `suburb` and `city_district` map to city, and its `level`,
  `staircase` and `entrance` map to units. A different mapping would move some figures.
- **Speed figures** come from one machine under WSL2, with the reference memory profile not enforced.

## 11. How to reproduce, and how to add a parser

```sh
uv sync
tools/libpostal/build.sh            # the pinned libpostal build (about 3 GB), or --verify an existing one
just rescore runs/2026-11-16        # score the committed predictions again: rewrites results.md/json, git diff shows no change
just all                            # a new full run (fetch, convert, predict, score, speed) into runs/<date>/
uv run python -m tools.report.breakdown runs/2026-11-16   # the tables in sections 7.5 and 9
```

`just all` needs a clean tree and takes about 4 minutes on the machine above. The external sets are downloaded by
script and checked by SHA-256 (`tools/sets/fetch.py`). The golden set ships in `sets/golden/gold/` with invented
values. `tools/label/direction.py` and `breakdown --real` read the private text, which only the owner has.

To add a parser, follow `adapters/README.md` ("Adding a parser"):

1. Write an adapter that returns character spans in the parser's own labels.
2. Write a mapping file from those labels to the schema.
3. Add the adapter to the registry and the conformance test.
4. Pin its version.
5. Run `tools/check.sh`, then `just all` on a new date.

A parser's own test files go in as a home set, reported apart.

## 12. References

- Barrentine, A. (2017). *Statistical NLP on OpenStreetMap, Part 2: libpostal 1.0*. Mapzen blog.
  <https://mapzen.com/blog/libpostal-1-0/>. Code: openvenues/libpostal, <https://github.com/openvenues/libpostal>.
- DataMade. *usaddress*. <https://github.com/datamade/usaddress> (version 0.5.16 used).
- Efron, B. (1979). Bootstrap methods: another look at the jackknife. *The Annals of Statistics* 7(1), 1–26.
  doi:10.1214/aos/1176344552.
- Federal Geographic Data Committee (2011). *United States Thoroughfare, Landmark, and Postal Address Data Standard*,
  FGDC-STD-016-2011. <https://fgdc.gov/standards/projects/address-data>.
- Gaere, E. (2026). *MESSY STREETS: A benchmark for geocoding real-world addresses*. arXiv:2609.01612. Issue #9 gives
  the DOI 10.1145/3841645.3843362, which could not be resolved when this was written. Cited only, not used.
- Lafferty, J., McCallum, A. and Pereira, F. (2001). Conditional random fields: probabilistic models for segmenting and
  labeling sequence data. *Proceedings of the 18th International Conference on Machine Learning*, 282–289.
- *python-crfsuite*, a Python binding to CRFsuite. <https://github.com/scrapinghub/python-crfsuite> (version 0.9.12 used).
- Senzing. *libpostal-data* (model and test data, 1.2.0). <https://github.com/Senzing/libpostal-data>.
- U.S. Department of Transportation. *National Address Database*. <https://www.transportation.gov/gis/national-address-database>.
- United States Postal Service. *Publication 28: Postal Addressing Standards*. <https://pe.usps.com/text/pub28/28c2_toc.htm>.
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the
  American Statistical Association* 22(158), 209–212. doi:10.1080/01621459.1927.10502953.
- Yin, Z., Li, D. and Goldberg, D. W. (2023). *Is ChatGPT a game changer for geocoding: a benchmark for geocoding
  address parsing techniques*. arXiv:2310.14360. Data: <https://github.com/zhengcongyin/geocoding-address-parsing-benchmark>.
