# Senzing test data, US rows: manifest

**Source:** `test_data_v1.2.0.csv` from Senzing's libpostal test data (12,868 rows, 2,233 with `country_code=us`), kept in
doorplate's `local-data/senzing-libpostal-test/` (`$SENZING_TEST_DATA`). **License:** mixed provenance (OpenStreetMap, libpostal's
tests, bug reports), so it is **not shipped**: `tools/sets/senzing_us.py` reads it and checks it by SHA-256 first. `python -m tools.sets.fetch senzing-us` downloads
`files/tests/v1.2.0/test_data.csv` from Senzing/libpostal-data at commit `fa19eff80e28c517956274c90479a017b3f63557` (tag 1.2.0;
Apache-2.0 repository) into `build/sources/`.

## Checksums (SHA-256)

- Source `test_data_v1.2.0.csv`: `db58065bf7508b862e9c6ee68774312bfc7e675192e21b8ee6aa9f7aa32ed51a`
- Converted `build/sets/senzing-us.jsonl.gz`: `71f55f77ca4421fe4ac11375b2ec6a57349e99cc349ddef8b2f7a19e2d73e8eb`

## Parts

| Part | Source value | Records | Aggregate |
|---|---|---|---|
| `osm` | `osm` | 2,172 | neutral |
| `bug` | `Libpostal-bug` | 6 | reported apart: cases reported as libpostal bugs, so drawn from its failures |

2,178 convert; 2 dropped (a component value not found in the string, one per part). The 53 `source=libpostal` rows are
libpostal's `test_us_parses` (set `libpostal-us`) and are excluded here; the converter stops if their texts differ from that set's.

Gold is libpostal-style component labels per row, mapped by `adapters/mappings/libpostal.toml`; the labels were made by
libpostal-trained or OSM-derived tooling, so libpostal is close to a home parser here too, stated beside every figure.
