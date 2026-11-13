# Geocode benchmark `dev` split: manifest

**Source:** [zhengcongyin/geocoding-address-parsing-benchmark](https://github.com/zhengcongyin/geocoding-address-parsing-benchmark)
at commit `424f94167c21d1ad3f8e70b50a75174f68dfe1f0`, `dev.txt` (IOB tags; paper arXiv 2310.14360). **License: none stated**, so the file
is **not shipped**: `tools/sets/geocode_dev.py` reads it (`$GEOCODE_BENCHMARK`; default doorplate's `local-data/geocode-benchmark/`)
and checks it by SHA-256 first. `python -m tools.sets.fetch geocode-dev` downloads
`benchmark_dataset/dev.txt` at that commit into `build/sources/` and checks it.

The `test` split is excluded: doorplate's rules were written while reading it.

## Checksums (SHA-256)

- Source `dev.txt`: `a3276155202126cf5604c576672c0ac8604eb9ba359350542b8e38a14cd50b79`
- Converted `build/sets/geocode-dev.jsonl.gz`: `bb9aafd04f469d960eae6638d768c654557dd1f15e73a31c9817240a82f941d0`

## Parts

| Part | Records | Aggregate |
|---|---|---|
| `dev` | 60,522 | neutral |

None dropped. Street addresses only (no units, PO boxes or routes), uppercase, one line, no commas, with input errors and
variants mined from a geocoder's logs. Gold has eight fields (house number, pre- and post-direction, street, road type,
city, state, ZIP); tags go to usaddress's names as doorplate's `convert.py` does, then through `adapters/mappings/usaddress.toml`.
The tokens are joined with single spaces to make the string.
