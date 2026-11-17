# doorplate releases on the showdown

A short appendix to the [v0.1.0 report](REPORT.md). It shows what each doorplate release scores on the same sets and gold, so
doorplate's authors have a curve and not one point. It is not part of the report and does not change it.

**Method.** The doorplate adapter was run on the highest point release of each minor version (0.1.0, 0.2.0, 0.3.1, 0.4.1,
0.5.1, 0.6.2; the earlier `0.x.0` builds and the unreleased `0.6.3` were not run), from the PyPI wheels. Each release ran
on the sets of the pinned run `2026-11-16` (every set's SHA-256 checked equal), scored by the same scorer and formula
(version 1) with the usaddress and libpostal predictions of that run reused unchanged, so only doorplate varies. Speed is
from one session on the same machine, pinned to 4 CPUs. Everything is in `runs/doorplate-releases/`; `uv run python -m
tools.releases` adds a release that is not there yet and rebuilds the table, so this page grows by a row and a line below.

| Release | Parser Score (95% interval) | Field F1 score (95% interval) | golden normal accuracy | golden hard accuracy | golden nightmare accuracy | Strings/s, 1 process | Strings/s, 4 processes | Install MB |
|---|---|---|---|---|---|---|---|---|
| 0.1.0 | 87.3 (86.0 to 88.4) | 96.4 (96.0 to 96.7) | 94.0 | 88.5 | 54.0 | 31,433 | 95,084 | 4.1 |
| 0.2.0 | 87.3 (86.0 to 88.4) | 96.4 (96.0 to 96.7) | 94.0 | 88.5 | 54.0 | 39,736 | 130,439 | 4.1 |
| 0.3.1 | 87.6 (86.3 to 88.8) | 96.6 (96.2 to 96.9) | 94.0 | 88.5 | 54.0 | 39,275 | 123,812 | 4.2 |
| 0.4.1 | 88.7 (87.5 to 89.9) | 96.9 (96.6 to 97.3) | 94.3 | 90.5 | 57.1 | 41,143 | 146,475 | 4.9 |
| 0.5.1 | 89.4 (88.2 to 90.6) | 97.2 (96.9 to 97.5) | 94.6 | 91.0 | 60.2 | 73,944 | 222,199 | 4.8 |
| 0.6.2 | 90.9 (89.7 to 92.0) | 97.6 (97.3 to 97.9) | 94.8 | 91.2 | 69.0 | 113,315 | 317,934 | 6.4 |
| usaddress 0.5.16 (from 2026-11-16) | 84.7 (83.4 to 86.0) | 95.7 (95.3 to 96.1) | 93.6 | 88.5 | 51.3 | 8,952 | 28,054 | 4.8 |
| libpostal 25099c5066 (from 2026-11-16) | 80.8 (79.5 to 82.2) | 93.4 (92.8 to 93.9) | 91.8 | 70.9 | 54.0 | 14,577 | 43,951 | 2,993.1 |

Intervals are 95% bootstrap intervals; releases less than about 1.5 points apart overlap, so read the curve, not a single step.
The usaddress and libpostal rows are single readings from 2026-11-16 (speed from that run's session, not this one).

## What changed between releases

Read from doorplate's `CHANGELOG.md`; the score movements are this benchmark's, not the changelog's.

- **0.1.0 to 0.2.0:** new API and documentation, no change to what any input parses to. Same score and accuracy, as expected.
  Speed differs only by session noise or by changes outside the parser.
- **0.3.1 (0.3.0 not run):** a batch of parsing rules found by running the parser over about 146 million address rows; the
  changelog reports the geocode benchmark going from 92.6% to 94.4%. Here the Parser Score rises 0.3 points (87.3 to 87.6)
  and the golden accuracies do not move.
- **0.4.1 (0.4.0 not run):** 0.4.1 itself adds tooling and a custom layer with no parse change, so the gain (+1.1 points) comes
  from 0.4.0's rules, mainly on the golden hard (88.5 to 90.5) and nightmare (54.0 to 57.1) parts.
- **0.5.1 (0.5.0 not run):** the key changes held for `k4` and the other 0.5.x work; Parser Score +0.7, nightmare +3.1 points,
  and speed up by about 80%.
- **0.6.2 (0.6.0 and 0.6.1 not run):** the `k5` key release and two speed releases, with no output change in 0.6.1 and 0.6.2.
  Parser Score +1.5 points, nightmare 60.2 to 69.0, and about 53% more strings per second than 0.5.1. The 0.6.2 score
  (90.9) equals the committed 0.6.0 run's (the project's v0.1.0 figure), as the changelog's byte-identical claim implies.

## Caveats

- These are today's sets, gold and conventions applied to old parsers. They are not what the project would have measured at
  the time.
- Parts of the golden set (its draw and exclusion strings) were built using doorplate's local data from recent versions, so
  the early releases are measured on strings chosen with later ones in view. Nothing was tuned to this.
- usaddress and libpostal are single readings; any "ahead of usaddress since release X" statement uses those fixed numbers.
  On the Parser Score, doorplate's interval first clears usaddress's at 0.4.1 (87.5 to 89.9 against 83.4 to 86.0); 0.3.1 is
  close (86.3 to 88.8).
- Gold, conventions and formula are unchanged by this work. If the `number-letter` reading (#47) changes, rescore every
  release on the new gold in the same pass.
- Install size here is the wheel's installed files, one release each; speed is one session, so small speed differences
  (0.1.0 to 0.3.1) are not meaningful.
