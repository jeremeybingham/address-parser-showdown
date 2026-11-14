# Golden set: manifest

Seed 20261112. 1,500 unlabeled records in 6 rounds of 250, drawn by `tools/golden/sample.py`
(composition: `COMPOSITION.md`). doorplate 0.6.0 supplied the anonymizer. Every
address is invented or anonymized: house numbers and street names are made up; city, state and ZIP are real.
This set is not "home" for any parser. It has no labels yet (steps 3 onward).

## Checksums (SHA-256)

- `round-1.jsonl`: `01c98835ee9074570ae444f178ef3853f14d71714bf00f59f8e8786c76687982`
- `round-2.jsonl`: `d7062b913a24f332ca5b315775b275660fd263c31a81e95d6104f49a4223965d`
- `round-3.jsonl`: `0a619ec1a83e2d96437a3aa24c1cbfefbd87b30f136e5c7a278fe15a31c85fe0`
- `round-4.jsonl`: `792112f3efa279f8ca080de12ab67d2088c14564565a86287f5a94fb17c3dd12`
- `round-5.jsonl`: `0995a466375b0cf955dbf528ff19fe8fffd75a5d56e8415a79bea13906e69e4a`
- `round-6.jsonl`: `adb211cbbfd1657f8cd4ec30cb745355278fe98a6f1c50a37fc42f06541fb463`
- `provenance.jsonl` (all rounds, current): `d17d1856ea46f8349844dc386bf8b36407469be0452260c37f7badd966c812fa`

## Records by stratum

| Stratum | Records |
|---|---|
| clean | 247 |
| public | 555 |
| template | 600 |

## Records by source

| Source | Records |
|---|---|
| fcc-amateur | 60 |
| fmcsa | 60 |
| nad | 502 |
| ny-corps | 60 |
| tdlr | 60 |
| template | 600 |
| va-scc | 60 |

## Records by shape

| Shape | Records |
|---|---|
| as-found | 555 |
| care-of | 19 |
| directional | 48 |
| fraction | 26 |
| general-delivery | 2 |
| highway | 79 |
| hyphen-number | 17 |
| number-letter | 31 |
| ordinary | 247 |
| po-box | 88 |
| rural-route | 52 |
| street-plain | 112 |
| street-unit | 126 |

## Records by style

| Style | Records |
|---|---|
| lower | 33 |
| mixed-commas | 491 |
| mixed-nocommas | 37 |
| nocomma | 81 |
| none | 260 |
| nostate | 35 |
| nozip | 26 |
| typo | 68 |
| upper | 97 |
| upper-commas | 178 |
| upper-nocommas | 96 |

## Exclusion string check

Every record was compared (lowercase, letters and digits only; whole text and first line) with 7 corpus
locations; passes. Strings read per location:

- `/home/jeremey/projects/temp-postal/doorplate/tests/corpus`: 12,447
- `/home/jeremey/projects/temp-postal/doorplate/tests/external`: 9,089
- `/home/jeremey/projects/temp-postal/doorplate/benchmarks/suite/v1`: 381,962
- `/home/jeremey/projects/temp-postal/doorplate/local-data/benchsuite/usaddress-training:synthetic_clean_osm_data.xml:ParseError`: 0
- `/home/jeremey/projects/temp-postal/doorplate/local-data/benchsuite/usaddress-training`: 113,280
- `/home/jeremey/projects/temp-postal/doorplate/local-data/geocode-benchmark`: 626,805
- `/home/jeremey/projects/libpostal-senzing/src/test`: 819

Candidates dropped while drawing (counts only): {"fcc-amateur:duplicate": 5, "fcc-amateur:leak-or-unfaithful": 9, "fmcsa:duplicate": 46, "fmcsa:leak-or-unfaithful": 16, "nad:duplicate": 1, "nad:leak-or-unfaithful": 112, "ny-corps:duplicate": 17, "ny-corps:leak-or-unfaithful": 28, "tdlr:duplicate": 11, "tdlr:leak-or-unfaithful": 9, "template:excluded": 9, "va-scc:duplicate": 28, "va-scc:leak-or-unfaithful": 45}.
libpostal's training data is not on disk here and could not be checked; its test sources under `src/test` were.

<!-- round-7 begin -->
## Round 7 (`hard`, added)

Seed 20261114, drawn by `tools/golden/hard.py`: 299 unlabeled records in 16 `hard` classes (sizes in `SIZE`: 30 for each
of the six added shape classes, 20 for the non-addresses, 11 for each of nine base `hard` classes). Every string is
invented; city, state and ZIP are real. The class is the shape the string was written from, never a parser run.

- `round-7.jsonl`: `803ec5d8076d9cbaafcb3af4635e2c26684e272cbd16717c8e096e04cdc11c6e`
- `provenance.jsonl` (all rounds): `39fec47656c966b125fad826daebb66802718e53ad536cbff7ac121a2187f5de`

| Class | Records |
|---|---|
| box-and-street | 11 |
| care-of | 11 |
| fraction | 11 |
| general-delivery | 11 |
| hyphen-number | 11 |
| named-place | 11 |
| no-street | 11 |
| non-address-hard | 20 |
| pre-type | 30 |
| rural-route | 11 |
| state-spelled | 30 |
| two-units | 30 |
| typo | 11 |
| typo-glued | 30 |
| typo-type | 30 |
| zip4-plain | 30 |
<!-- round-7 end -->

<!-- round-8 begin -->
## Round 8 (`nightmare`, issue #22)

Seed 20261113, drawn by `tools/golden/nightmare.py`: 264 unlabeled records, (class, variant) cells of 9 unless `SIZE` says otherwise
for 18 paired classes (cell sizes in `SIZE`, equal for the two variants of a class). Every string is invented; city, state and ZIP are real. The variant is set by the form that
wrote the string, never by a parser run (`COMPOSITION.md`, "`nightmare` classes are paired").

- `round-8.jsonl`: `212a194f599060af6c7fec4207409a54a8c4fd416806dd2b130e3a4ef08c380a`
- `provenance.jsonl` (all rounds, with `variant` and `tracker` on round 8): `39fec47656c966b125fad826daebb66802718e53ad536cbff7ac121a2187f5de`

| Share | Records |
|---|---|
| covered | 132 |
| adjacent | 132 |
| doorplate-research classes | 126 (48%) |
| outside classes | 138 (52%) |

Outside `adjacent` records by the tracker the shape came from (cap one third each; Pub 28 forms excluded, 60 records):
doorplate 33%, usaddress 33%, libpostal 33%.

| Class | Records |
|---|---|
| box-glued | 12 |
| county-road-compass | 18 |
| fraction-form | 16 |
| grid-utah | 16 |
| grid-wisconsin | 4 |
| highway-lettered | 16 |
| intersection | 4 |
| letter-before-street | 18 |
| lot-trailer-site | 24 |
| military | 18 |
| no-so-direction | 18 |
| non-address-nightmare | 12 |
| paren-unit | 18 |
| second-number | 18 |
| spelled-number | 12 |
| unit-before-street | 18 |
| urbanization | 4 |
| zip4-cut | 18 |
<!-- round-8 end -->

<!-- round-11 begin -->
## Placeholder-city cards dropped, round 11 added (2026-11-14)

The National Address Database holds a placeholder (`Not stated`) in its city field for some rows. A card whose whole city
field is one of doorplate's `[city_placeholder]` phrases (`crates/doorplate/data/special.toml`) is not part of the set.
98 cards of rounds 1 to 6 were dropped ({"clean/nad": 53, "public/nad": 45}); their ids are not reused, so the
other cards keep their ids and labels. Round 11 holds 98 replacements, the next unused rows of the same sources'
walks (same stratum and source as the card each replaces; own random generator `seed + 11`; no placeholder city, a
duplicate or an exclusion hit skipped). Rounds 1 to 6 now hold 1402
cards, round 11 98. Round 9 drops its placeholder-city rows as well (counted in its section).

- `round-11.jsonl`: `fd9acdd63324309098096292e7cf931e5cdb2475187ad0554bcc88dc4151fe10`
- `provenance.jsonl` (all rounds): `d17d1856ea46f8349844dc386bf8b36407469be0452260c37f7badd966c812fa`
<!-- round-11 end -->

<!-- round-9 begin -->
## Round 9 (restored rows, issue #26)

Seed 20261112, drawn by `tools/golden/sample.py --restore`: 165 unlabeled records, the rows the seed-20261112 walk
dropped as `leak-or-unfaithful` (the `Anonymizer` filter), taken in the same hash order, and
no anonymizer call on them. A row of a messy source keeps the source's own city, state and ZIP (case, ZIP+4) with no dice
style (style `as-written`, issue #26 item 3); NAD rows keep the draw's style rule. Rounds 1 to 6 are unchanged (the redraw reproduces them byte for byte). The duplicate and
exclusion-corpus drops stay: {"fmcsa:duplicate": 7, "nad:placeholder-city": 12, "ny-corps:duplicate": 10, "tdlr:duplicate": 1, "va-scc:duplicate": 23, "va-scc:excluded": 1}. Each record keeps the stratum and source of its
walk and has `restored: true` in `provenance.jsonl`.

**No text ships for this round.** These rows are not anonymized, so `sets/golden/rounds/round-9.jsonl` does not exist;
the cards are labeled on the row's own text (`local-data/golden-real/rounds/round-9.jsonl`, git-ignored) and the shipped
text is made from the labels by `tools/golden/derive.py`, which holds a card back when a real word is left outside a
kept label (the count held is added here after derivation).

- ids of round 9 (`provenance.jsonl` rows with `round` 9), SHA-256 of those rows: `10a7bf936db98f561122924e7a2351310e5115fea89e0216dd413136c142733b`
- `provenance.jsonl` (all rounds): `9f8112d8eb0f75a5254bd3032dd8c4dfbd3122dc6a712340ba4ed8dc201819cc`

| Stratum | Records |
|---|---|
| clean | 48 |
| public | 117 |

| Source | Records |
|---|---|
| fcc-amateur | 9 |
| fmcsa | 9 |
| nad | 100 |
| ny-corps | 18 |
| tdlr | 8 |
| va-scc | 21 |

| Style | Records |
|---|---|
| as-written | 65 |
| mixed-commas | 69 |
| mixed-nocommas | 8 |
| upper-commas | 18 |
| upper-nocommas | 5 |
<!-- round-9 end -->
