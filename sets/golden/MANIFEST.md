# Golden set: manifest

Seed 20261112. 1,500 unlabeled records in 6 rounds of 250, drawn by `tools/golden/sample.py`
(composition: `COMPOSITION.md`). doorplate 0.6.0 supplied the anonymizer. Every
address is invented or anonymized: house numbers and street names are made up; city, state and ZIP are real.
This set is not "home" for any parser. It has no labels yet (steps 3 onward).

## Checksums (SHA-256)

- `round-1.jsonl`: `01c98835ee9074570ae444f178ef3853f14d71714bf00f59f8e8786c76687982`
- `round-2.jsonl`: `d7062b913a24f332ca5b315775b275660fd263c31a81e95d6104f49a4223965d`
- `round-3.jsonl`: `ae1fbb7aa6299f19a1458af677b30e84d97c46707f59b20ae7bf8ea991497e70`
- `round-4.jsonl`: `511e3211412ee706bf8e787e00231bca26c9743ed5c1ff36be68b81cd30090dc`
- `round-5.jsonl`: `48af7ae167d62f4244d140ee27778aabdfa68d5bb171f592e8175c7a52fbcec8`
- `round-6.jsonl`: `588c05890d7669f71a4ac57032877fa0e8ad1330f7b53ea9ebb942bb48d32880`
- `provenance.jsonl` (all rounds, current): `92b78f928638bdbd38b23e0c6ef793bc3cdb23e9a616d25f26402dbe13ef1427`

## Records by stratum

| Stratum | Records |
|---|---|
| clean | 247 |
| public | 555 |
| template | 594 |

## Records by source

| Source | Records |
|---|---|
| fcc-amateur | 60 |
| fmcsa | 60 |
| nad | 502 |
| ny-corps | 60 |
| tdlr | 60 |
| template | 594 |
| va-scc | 60 |

## Records by shape

| Shape | Records |
|---|---|
| as-found | 555 |
| care-of | 19 |
| directional | 48 |
| fraction | 26 |
| general-delivery | 2 |
| highway | 73 |
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
| none | 257 |
| nostate | 35 |
| nozip | 26 |
| typo | 68 |
| upper | 94 |
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

<!-- round-11 begin -->
## Cards dropped from rounds 1 to 6, round 11 added (2026-11-14)

Two kinds of card are not part of the set, and their ids are not reused (the other cards keep their ids and labels):

- **Placeholder city** (98 cards, all NAD): the whole city field is one of doorplate's `[city_placeholder]` phrases
  (`Not stated`, `Unknown`, ...; `crates/doorplate/data/special.toml`).
- **Frontage road** (6 cards, `template`/`highway`, rounds 3 to 6): `Interstate N Frontage Rd` was one of nine
  `highway` variants, so frontage roads were about 1% of the template stratum against 0.017% of NAD. Rounds 1 and 2 were
  already labeled, so their frontage cards stay.

Round 11 holds 104 replacements: for a placeholder card, the next unused row of the same source's walk (no
placeholder city; own generator `seed + 11`); for a frontage card, a `highway` template card with no frontage road (own
generator `seed + 12`). Duplicates and exclusion hits are skipped. Rounds 1 to 6 now hold
1396 cards. Round 9 drops its placeholder-city rows as well.

- `round-11.jsonl`: `1b50eadb87f45a774074047c3cd6a6f2e3d38b6c924c01b094da95fb014f6324`
- `provenance.jsonl` (all rounds): `f9c7b31a9b413c47439267b9bbadbf9bc57117ddc5c0a56b29800e971349575e`
<!-- round-11 end -->

## Removed cards and round 12 (2026-11-14)

35 cards of rounds 7 and 8 are removed (`removed.jsonl`; see `COMPOSITION.md`). Round 12 (30 real cards, private text, not
in `sets/golden/rounds/`) is drawn by `tools/golden/realforms.py`; its rows are in `provenance.jsonl` (stratum `real`).
- `removed.jsonl`: `a7e5b763353f17f1f650f247338afc2451a940eb19cdd631baf9e77c07017b51`
- `provenance.jsonl` (all rounds): `92b78f928638bdbd38b23e0c6ef793bc3cdb23e9a616d25f26402dbe13ef1427`

## Shipped gold, rounds 1 to 12 (2026-11-15)

All rounds were labeled blind and adjudicated (rounds 1 to 12, 1,296 cards queued, every one decided). 34 more cards the
owner marked "remove" were added to `removed.jsonl` (now 69; 27 non-address, 1 grid, 6 other). Shipped cards per round
(`derive` holds back a card that would ship a real word):

| Round | Shipped | Held |
|---|---|---|
| 1 | 235 | 0 |
| 2 | 234 | 0 |
| 3 | 232 | 0 |
| 4 | 234 | 0 |
| 5 | 225 | 0 |
| 6 | 233 | 0 |
| 7 | 270 | 0 |
| 8 | 230 | 0 |
| 9 | 163 | 0 |
| 10 | 249 | 0 |
| 11 | 104 | 0 |
| 12 | 30 | 0 |

Shipped: **2,439** cards; held: 0 (14 held for a common place or road word; the owner cleared them to ship, `OWNER_OK` in `derive.py`). Round 10 had no provenance rows (added by `tools/golden/sba.py`); round 11's rows were
written from renumbered cards, with 4 ids repeated and 4 missing (fixed in `tools/golden/sample.py`).
- `gold/round-1.jsonl`: `0b1b3898f311a30c6db31d77dc848d9fc3ea4a51e815d25c6e9331efc86b9c81`
- `gold/round-2.jsonl`: `0ce3716ad1d5da8a40f88312fb72ff3b51450180bbd43dbd489ab0fa5847d046`
- `gold/round-3.jsonl`: `ceb591f2ada5f1254c7a5cfddfeb4d65d090f76c0ba13ffb1748124ae1b64031`
- `gold/round-4.jsonl`: `9e5c989befb56799de93c3c12db8d60d713ddf4e36c2a962b6a3207ccf91eab4`
- `gold/round-5.jsonl`: `1b404d19f29b36e2500f9e42b41c503129d98cb4012be9ab6963e6e62f02425f`
- `gold/round-6.jsonl`: `897bfd0a0f6779017051357d4b03988e30ae88a655f4538e7dc01134319a8cac`
- `gold/round-7.jsonl`: `afa6926f24a511636116c83edccc7aaba646bc29c556f14210b7c757facbdf81`
- `gold/round-8.jsonl`: `32912a021741c00985a87d9ffc5d0af715c517ed510f289627e618c8b06dbc58`
- `gold/round-9.jsonl`: `93d4061189dc06ede2d681a23a434b764fa0a993802e6fbeb6d99f84bb6435c6`
- `gold/round-10.jsonl`: `5695049cfb91e27d2b62303c45077be27dd2e62cdcc3cb6bacfdf90fdc876bee`
- `gold/round-11.jsonl`: `b332326e75ab3a992e6bf5224c798d3d59093f1a3681517c1a573bbcc8ed009b`
- `gold/round-12.jsonl`: `9df2d85a2e6533f5371b99956cdd171fbee98853e714849c4026a99a10b669b5`
- `removed.jsonl`: `a7e5b763353f17f1f650f247338afc2451a940eb19cdd631baf9e77c07017b51`

## Adjudication figures (2026-11-15)

Parser-neutral: they count how often the owner changed a card after seeing anonymous parser readings, and say nothing
about any one parser. Per-parser agreement is left to the scorer (#6), so no parser's number is read before the formula
is fixed. Counts are over the 2,439 shipped cards (private logs; no text).

| Measure | Cards | Share |
|---|---|---|
| Queued (some parser read the card differently from the blind gold) | 1,264 | 51.8% of 2,439 |
| Spans changed in adjudication | 579 | 23.7% of 2,439; 45.8% of the queued |
| Doubtful mark changed in adjudication | 12 | 0.5% |
| Cards no parser disagreed on | 1,175 | 48.2% |

Per round, queued / spans changed: 1: 108 / 56, 2: 109 / 58, 3: 110 / 56, 4: 108 / 56, 5: 112 / 59, 6: 103 / 51, 7: 185 / 58,
8: 203 / 49, 9: 70 / 44, 10: 96 / 62, 11: 39 / 30, 12: 21 / 0 (round 12 was pre-labeled from source fields; every
queued card was kept).

Reading it: a queued card is one where some parser differed, not an error in the gold, and about half of the queued
cards were kept as labeled. The 579 changes are the cases where the owner judged the gold wrong or less defensible than
the other reading. The gold is therefore shaped in part by what the parsers did, one reason the report states the share
and lists the changed cards by round. Cards were not shown with a parser name.
