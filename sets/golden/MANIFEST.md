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
