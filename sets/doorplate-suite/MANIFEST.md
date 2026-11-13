# doorplate benchmark suite v1: manifest

**Source:** doorplate's benchmark suite v1, `benchmarks/suite/v1/compare.jsonl.gz` at commit
[`3fc5ec4`](https://github.com/jeremeybingham/doorplate/tree/3fc5ec4fd79c62f345b7421ea9af9857d123cdc2/benchmarks/suite/v1)
(the commit that froze v1; doorplate's own manifest there gives the build, seed and composition).
**License:** Apache-2.0 (doorplate). The addresses come from the National Address Database and TIGER (US public domain)
plus 1,000 hand-written records. **Not shipped here:** `tools/sets/doorplate_suite.py` reads the file from a doorplate
checkout (`$DOORPLATE_HOME`) or downloads it with `--fetch`, and checks it by SHA-256 first.

## Checksums (SHA-256)

- Source `compare.jsonl.gz`: `2336f0996f2d044d56d69467f6f3ea7d33a4a64a680decb43179651bf006b430`
- Converted `build/sets/doorplate-suite.jsonl.gz`: `c0c068963ca3432ccce741218bfae43eab529ce68e3bb48197d7981be140990d`

## Parts

| Part | Records | Aggregate |
|---|---|---|
| `natural` | 16,001 | neutral: in the Parser Score's "other neutral sets" |
| `hand` | 1,000 | neutral: in the Parser Score's "other neutral sets" |
| `hard` | 2,585 | reported apart, out of every aggregate: drawn from the blind spots of two of the three parsers |

**Home set:** the plan (issue #5) treats no part as a home set, but doorplate's author built the suite, and that is
stated beside every figure from it. Its build excluded usaddress's test and training files and the geocode benchmark
splits (doorplate's suite README). The `natural` part is NAD-derived, and libpostal was trained on OpenAddresses, which overlaps NAD
(`METHODOLOGY.md`).

## Conversion

The suite's gold is token labels in usaddress's names. They map to the schema by `adapters/mappings/usaddress.toml`
(a table of label names; usaddress's output is not used), and neighbouring tokens with the same label join into one span
(`PELL` + `CITY` is one `city` span; a comma keeps two apart). All 19,586 records convert; none are dropped.

- `StreetNamePreModifier` (83 tokens) maps to the coarse `street`: those spans are scored on the coarse track only.
- The gold follows doorplate's labeling, not this repository's conventions list (`schema/conventions.toml`); the scorer
  applies the conventions to every set alike (step 5).
- Kept per record for slicing: `source` (`nad`, `tiger`, `synthetic`, `hand`), `type` (street, PO box, rural, highway,
  military, general delivery) and `style`.
