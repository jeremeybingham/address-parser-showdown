# tools/sets

Step 4 (issue #5): the existing test sets, each converted to one record format and run through every adapter.

```sh
uv run python -m tools.sets.doorplate_suite          # build/sets/doorplate-suite.jsonl.gz (--fetch to download it)
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

Adding a set: a converter here that checks its source by SHA-256 and writes through `common.write_jsonl`; a folder in
`sets/` with `MANIFEST.md` (source, license, counts, checksums, home parts); a row above and in `sets/README.md`.
