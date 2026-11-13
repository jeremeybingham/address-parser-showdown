# Golden set: manifest

Seed 20261112. 1,500 unlabeled records in 6 rounds of 250, drawn by `tools/golden/sample.py`
(composition: `COMPOSITION.md`). doorplate 0.6.0 supplied the anonymizer. Every
address is invented or anonymized: house numbers and street names are made up; city, state and ZIP are real.
This set is not "home" for any parser. It has no labels yet (steps 3 onward).

## Checksums (SHA-256)

- `round-1.jsonl`: `b6f7dff4c9c6d6e09ab8be949e4a56941d4cc4942f5a87acd04987074d765c83`
- `round-2.jsonl`: `4e1852a42423782a21fc667982640720b9db0373dfff7680c22320730b1315a9`
- `round-3.jsonl`: `8ac64b1083304da0427b1d0b5b714346ed300c94868389b88f6eb2f921cad402`
- `round-4.jsonl`: `d712bdc52bf6ff241a27cefcfbd4489846968887f5357702fb1b07c1be5990b8`
- `round-5.jsonl`: `9a6e4a5572c46538c21d4c2909da0b84d0e0989afaa423dff110da0f14e80260`
- `round-6.jsonl`: `94d1d7f82b5b3fa9506265620b27dd95e07b1d12a174bf332c371b4a7498f55b`
- `provenance.jsonl` (all rounds, current): `39fec47656c966b125fad826daebb66802718e53ad536cbff7ac121a2187f5de`

## Records by stratum

| Stratum | Records |
|---|---|
| clean | 300 |
| public | 600 |
| template | 600 |

## Records by source

| Source | Records |
|---|---|
| fcc-amateur | 60 |
| fmcsa | 60 |
| nad | 600 |
| ny-corps | 60 |
| tdlr | 60 |
| template | 600 |
| va-scc | 60 |

## Records by shape

| Shape | Records |
|---|---|
| as-found | 600 |
| care-of | 19 |
| directional | 48 |
| fraction | 26 |
| general-delivery | 2 |
| highway | 79 |
| hyphen-number | 17 |
| number-letter | 31 |
| ordinary | 300 |
| po-box | 88 |
| rural-route | 52 |
| street-plain | 112 |
| street-unit | 126 |

## Records by style

| Style | Records |
|---|---|
| lower | 33 |
| mixed-commas | 567 |
| mixed-nocommas | 39 |
| nocomma | 81 |
| none | 260 |
| nostate | 35 |
| nozip | 26 |
| typo | 68 |
| upper | 97 |
| upper-commas | 189 |
| upper-nocommas | 105 |

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

<!-- round-9 begin -->
## Round 9 (restored rows, issue #26)

Seed 20261112, drawn by `tools/golden/sample.py --restore`: 177 unlabeled records, the rows the seed-20261112 walk
dropped as `leak-or-unfaithful` (the `Anonymizer` filter), taken in the same hash order and with the same style rule, and
no anonymizer call on them. Rounds 1 to 6 are unchanged (the redraw reproduces them byte for byte). The duplicate and
exclusion-corpus drops stay: {"fmcsa:duplicate": 7, "ny-corps:duplicate": 10, "tdlr:duplicate": 1, "va-scc:duplicate": 23, "va-scc:excluded": 1}. Each record keeps the stratum and source of its
walk and has `restored: true` in `provenance.jsonl`.

**No text ships for this round.** These rows are not anonymized, so `sets/golden/rounds/round-9.jsonl` does not exist;
the cards are labeled on the row's own text (`local-data/golden-real/rounds/round-9.jsonl`, git-ignored) and the shipped
text is made from the labels by `tools/golden/derive.py`, which holds a card back when a real word is left outside a
kept label (the count held is added here after derivation).

- ids of round 9 (`provenance.jsonl` rows with `round` 9), SHA-256 of those rows: `c58cfe32d1c34007b2507347e3a223ad277a1a899b02c002325ba908d11cf86b`
- `provenance.jsonl` (all rounds): `230d3bbb116fd106f4d2dac0041376828858de4186f7b6513019f40c92cdb7b7`

| Stratum | Records |
|---|---|
| clean | 52 |
| public | 125 |

| Source | Records |
|---|---|
| fcc-amateur | 9 |
| fmcsa | 9 |
| nad | 112 |
| ny-corps | 18 |
| tdlr | 8 |
| va-scc | 21 |

| Style | Records |
|---|---|
| mixed-commas | 99 |
| mixed-nocommas | 12 |
| upper-commas | 45 |
| upper-nocommas | 21 |
<!-- round-9 end -->
