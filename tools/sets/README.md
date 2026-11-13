# tools/sets

Step 4 (issue #5): the existing test sets, each converted to one record format and run through every adapter.

```sh
uv run python -m tools.sets.doorplate_suite          # build/sets/doorplate-suite.jsonl.gz (--fetch to download it)
uv run python -m tools.sets.usaddress_tests          # likewise: libpostal_us, senzing_us, geocode_dev (local copies, checked by SHA-256)
uv run python -m tools.sets.predict doorplate-suite  # build/predictions/doorplate-suite/<parser>.jsonl.gz
```

**Record format** (`common.py`): `{"id", "text", "spans", "part", ...}`. `spans` are `[start, end, label]` with
canonical labels, as in the golden set's gold files; a coarse label stands where the source labels a field without its
parts. `part` is what a figure is reported on (a stratum or split); each set's `MANIFEST.md` says which parts are home
sets or out of the aggregate.

**Outputs** go to `build/` (git-ignored). Converters are deterministic (gzip with a fixed time, sorted keys), and the
set's `MANIFEST.md` records the SHA-256 of the converted file, so a rerun shows it produced the same set. Prediction
files hold `native` spans (the parser's own labels), canonical `spans` and `error` (an exception type), plus
`<parser>.versions.json` (versions, libpostal pin problems, timing). They are committed with the pinned run (step 7).

| Set | Converter | Source |
|---|---|---|
| [doorplate suite v1](../../sets/doorplate-suite/MANIFEST.md) | `doorplate_suite.py` | a doorplate checkout or `--fetch` (2 MB, pinned commit) |
| [usaddress tests](../../sets/usaddress-tests/MANIFEST.md) | `usaddress_tests.py` | usaddress's `measure_performance/test_data/` (six files, MIT), `$USADDRESS_TESTS` |
| [libpostal `test_us_parses`](../../sets/libpostal-us/MANIFEST.md) | `libpostal_us.py` | `test/test_parser.c` of the pinned clone, `$LIBPOSTAL_HOME` (read, not copied) |
| [Senzing test data, US rows](../../sets/senzing-us/MANIFEST.md) | `senzing_us.py` | `test_data_v1.2.0.csv`, `$SENZING_TEST_DATA` (not shipped) |
| [geocode benchmark `dev`](../../sets/geocode-dev/MANIFEST.md) | `geocode_dev.py` | `dev.txt`, `$GEOCODE_BENCHMARK` (not shipped, no license stated) |

The four sets after the first read local copies (no download); each checks its source by SHA-256 and stops on a
difference. The fetch scripts (a download with the same check) are not written yet: a rerun elsewhere needs the files in place.
Adding a set: a converter here that checks its source by SHA-256 and writes through `common.write_jsonl`; a folder in
`sets/` with `MANIFEST.md` (source, license, counts, checksums, home parts); a row above and in `sets/README.md`.
