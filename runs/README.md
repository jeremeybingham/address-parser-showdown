# runs

One folder per run (`runs/<date>/`), made by `just all` (`uv run python -m tools.run`) and never overwritten: a new run is a
new date, and an old run is not edited.

| File | Holds |
|---|---|
| `predictions/<set>/<parser>.jsonl.gz` | every adapter's output on every set (native and canonical spans), with `<parser>.versions.json` (parser versions, model checksum, the set's SHA-256, pin check) |
| `results.md`, `results.json` | the scorer's tables: record accuracy with Wilson intervals, field F1, the fine track, the Parser Score with its bootstrap interval, the sensitivity table |
| `speed.md`, `speed.json` | speed, load time, memory and install size (step 6), measured pinned to 4 CPUs |
| `run.json` | the commit that ran, whether the tree was clean, parser versions, each set's SHA-256, the host |

**Rescore without running a parser:** `just rescore runs/<date>` fetches and converts the sets (checksummed) and scores the
committed predictions again; the result is byte-identical to the committed `results.json`.

The run refuses to start on a dirty tree and refuses to finish if any parser build differs from its pin (`tools/libpostal/pins.env`,
`uv.lock`). Speed figures are from the machine named in `speed.md`; the 8 GB memory limit of the reference profile is not enforced
(libpostal's four processes hold about 11.8 GB together, so that row needs a larger machine).

Runs: `2026-11-15` (the first full pinned run, kept unchanged) and `2026-11-16` (the same predictions rescored after a scorer fix and the highway alternatives; the run the v0.1.0 report uses). The report's section 6.4 explains the difference.

`doorplate-releases/` is a separate appendix, not a pinned run: the doorplate adapter on the highest point release of each minor version
(`uv run python -m tools.releases`; a release with a folder is skipped, so a rerun after a new release adds only that one). usaddress and
libpostal predictions are reused from the reference run named in each `release.json`; `releases.md` is the table.
