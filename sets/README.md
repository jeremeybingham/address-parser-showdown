# sets

Every test set, each in its own folder with a `MANIFEST.md`: source, license, counts and checksums, and whether it is
a "home" set for any parser (reported, but out of every aggregate). Sets that are fetched by script rather than
shipped carry checksums so a rerun can prove it used the same file. 

| Set | State |
|---|---|
| [`golden/`](golden/MANIFEST.md) | 1,500 unlabeled records in six rounds (step 2); composition in [`golden/COMPOSITION.md`](golden/COMPOSITION.md); labels come in step 3; difficulty tiers `normal`/`hard`/`nightmare` (issue #14; rules in the composition page, class table in `tools/golden/tiers.py`) |
| [`doorplate-suite/`](doorplate-suite/MANIFEST.md) | doorplate's benchmark suite v1, 19,586 records (`natural`, `hand`; `hard` reported apart); read from a doorplate checkout or fetched, converted by `tools/sets/` |
| [`usaddress-tests/`](usaddress-tests/MANIFEST.md) | usaddress's own test files, 9,088 records in six parts; **home set for usaddress**; read from a local copy |
| [`libpostal-us/`](libpostal-us/MANIFEST.md) | libpostal's `test_us_parses`, 53 cases, read from the pinned clone; **home set for libpostal** |
| [`senzing-us/`](senzing-us/MANIFEST.md) | Senzing's test data, US rows without libpostal's own 53: 2,178 records (`osm`; `bug` reported apart); not shipped |
| [`geocode-dev/`](geocode-dev/MANIFEST.md) | the geocode benchmark `dev` split, 60,522 records; not shipped, no license stated |

Converters, the record format and running the adapters: `tools/sets/README.md`. Rebuild or re-check the golden set with `tools/golden/sample.py` (maintainers: it reads private
data in doorplate's `local-data/`).
