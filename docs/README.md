# Documentation

## Pages by topic

| Topic | Page |
|---|---|
| What the project is, layout | [`../README.md`](../README.md) |
| Fairness rules and method | [`../METHODOLOGY.md`](../METHODOLOGY.md) |
| Label schema and conventions | [`../schema/README.md`](../schema/README.md) |
| Adapters, the conformance test, how to add a parser, the pinned libpostal build | [`../adapters/README.md`](../adapters/README.md) |
| Sets and manifests | [`../sets/README.md`](../sets/README.md) |
| Scoring and the Parser Score | [`../scorer/README.md`](../scorer/README.md) |

## When you change something, check these

| You change | Check |
|---|---|
| A convention or a schema field | `schema/`; `METHODOLOGY.md`; every adapter mapping; the conformance test |
| An adapter or a pinned version | its mapping; the version pins; `runs/` (a new run, never an edit to an old one) |
| A set | its `MANIFEST.md` (counts, checksums); `sets/README.md` |
| The scorer or the formula | `METHODOLOGY.md` (a formula change after the first run is listed in the report) |
| Build commands, layout, CI | `AGENTS.md`; `CLAUDE.md`; `README.md`; this index |
| A page added, renamed or removed | this index |
