# sets

Every test set, each in its own folder with a `MANIFEST.md`: source, license, counts and checksums, and whether it is
a "home" set for any parser (reported, but out of every aggregate). Sets that are fetched by script rather than
shipped carry checksums so a rerun can prove it used the same file. 

| Set | State |
|---|---|
| [`golden/`](golden/MANIFEST.md) | 1,500 unlabeled records in six rounds (step 2); composition in [`golden/COMPOSITION.md`](golden/COMPOSITION.md); labels come in step 3; difficulty tiers `normal`/`hard`/`nightmare` are added by issue #14 (rules in the composition page) |
| [`doorplate-suite/`](doorplate-suite/MANIFEST.md) | doorplate's benchmark suite v1, 19,586 records (`natural`, `hand`; `hard` reported apart); read from a doorplate checkout or fetched, converted by `tools/sets/` |

Step 4 adds the rest (`tools/sets/README.md`: converters, the record format, running the adapters). Rebuild or re-check the golden set with `tools/golden/sample.py` (maintainers: it reads private
data in doorplate's `local-data/`).
