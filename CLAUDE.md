# CLAUDE.md

@AGENTS.md

This file holds the process we follow with Claude Code; the rules and commands are in `AGENTS.md` (imported above).
Machine facts and standing preferences are in `~/.claude/CLAUDE.md`.

## Workflow

- Before finishing a task run `tools/check.sh`; report anything that fails or was not run.
- Add a regression test for every bug fixed.
- Find the change in the table in `docs/README.md` (if present) and update every page it names in the same change.
- Keep `AGENTS.md` in step with the code: when commands, rules or layout change, update it in the same change.
- Pre-approved jobs (no need to ask even if they run long): none yet. Downloads (external sets, the libpostal model) need a go-ahead.
- Keep small commits; one PR per piece of related work, from a branch, with the PR template.

## Local notes

Project state (where things stand, next step, open decisions) is in `local-data/SESSION.md` (git-ignored); rewrite its
"Where things stand" block at the end of a session (`/handoff`).

## Private data

- Private data (source files, run outputs, notes about it) stays in `local-data/` (git-ignored). Never commit it.
- Never print personal data (names, whole rows) to the transcript, issues, PRs or docs. Output counts and shapes
  (letters to `a`, digits to `9`); examples are invented from scratch, never a real row with words changed.
- Scripts that read `local-data/` catch reader errors and print only the error type (`type(e).__name__`): DuckDB and
  pyarrow error messages quote source rows.
- Each source gets a folder with `NOTICE.md` (where it came from, license, how we may use it), `INVENTORY.md` (sizes,
  hashes, shapes) and its converter, plus a row in `local-data/README.md`.

@local-data/SESSION.md
