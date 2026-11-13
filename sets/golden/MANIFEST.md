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
- `provenance.jsonl`: `2017d1a9cbf949f3cf4782fb1af798da24ac13e2df588b5ed5582dd3178caefd`

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

<!-- round-8 begin -->
## Round 8 (`nightmare`, issue #22)

Seed 20261113, drawn by `tools/golden/nightmare.py`: 264 unlabeled records, (class, variant) cells of 9 unless `SIZE` says otherwise
for 18 paired classes (cell sizes in `SIZE`, equal for the two variants of a class). Every string is invented; city, state and ZIP are real. The variant is set by the form that
wrote the string, never by a parser run (`COMPOSITION.md`, "`nightmare` classes are paired").

- `round-8.jsonl`: `212a194f599060af6c7fec4207409a54a8c4fd416806dd2b130e3a4ef08c380a`
- `provenance.jsonl` (all rounds, with `variant` and `tracker` on round 8): `2cad3f542c7a3e671bb7b0462e1357e2fd1892800a5779f655e05a823f46a5a7`

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
