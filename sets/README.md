# sets

Every test set, each in its own folder with a `MANIFEST.md`: source, license, counts and checksums, and whether it is
a "home" set for any parser (reported, but out of every aggregate). Sets that are fetched by script rather than
shipped carry checksums so a rerun can prove it used the same file. 

| Set | State |
|---|---|
| [`golden/`](golden/MANIFEST.md) | 1,500 unlabeled records in six rounds (step 2); composition in [`golden/COMPOSITION.md`](golden/COMPOSITION.md); labels come in step 3 |

Steps 3 and 4 add the rest. Rebuild or re-check the golden set with `tools/golden/sample.py` (maintainers: it reads private
data in doorplate's `local-data/`).
