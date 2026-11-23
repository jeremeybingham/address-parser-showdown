# doorplate releases on the showdown (appendix)

The doorplate adapter on the highest point release of each minor version, on the sets and gold of `2026-11-16`. Made by `uv run python -m tools.releases`; a release with a folder here is not run again.

| Release | Parser Score (95% interval) | Field F1 score (95% interval) | golden normal accuracy | golden hard accuracy | golden nightmare accuracy | Strings/s, 1 process | Strings/s, 4 processes | Install MB |
|---|---|---|---|---|---|---|---|---|
| 0.1.0 | 87.3 (86.0 to 88.4) | 96.4 (96.0 to 96.7) | 94.0 | 88.5 | 54.0 | 31,433 | 95,084 | 4.1 |
| 0.2.0 | 87.3 (86.0 to 88.4) | 96.4 (96.0 to 96.7) | 94.0 | 88.5 | 54.0 | 39,736 | 130,439 | 4.1 |
| 0.3.1 | 87.6 (86.3 to 88.8) | 96.6 (96.2 to 96.9) | 94.0 | 88.5 | 54.0 | 39,275 | 123,812 | 4.2 |
| 0.4.1 | 88.7 (87.5 to 89.9) | 96.9 (96.6 to 97.3) | 94.3 | 90.5 | 57.1 | 41,143 | 146,475 | 4.9 |
| 0.5.1 | 89.4 (88.2 to 90.6) | 97.2 (96.9 to 97.5) | 94.6 | 91.0 | 60.2 | 73,944 | 222,199 | 4.8 |
| 0.6.2 | 90.9 (89.7 to 92.0) | 97.6 (97.3 to 97.9) | 94.8 | 91.2 | 69.0 | 113,315 | 317,934 | 6.4 |
| 0.7.0 | 91.8 (90.7 to 92.9) | 97.9 (97.6 to 98.1) | 94.9 | 92.4 | 73.0 | 105,833 | 309,258 | 6.4 |
| 0.7.1 | 91.8 (90.7 to 92.9) | 97.9 (97.6 to 98.1) | 94.9 | 92.4 | 73.0 | 113,770 | 334,536 | 6.5 |
| usaddress 0.5.16 (from 2026-11-16) | 84.7 (83.4 to 86.0) | 95.7 (95.3 to 96.1) | 93.6 | 88.5 | 51.3 | 8,952 | 28,054 | 4.8 |
| libpostal 25099c5066 (from 2026-11-16) | 80.8 (79.5 to 82.2) | 93.4 (92.8 to 93.9) | 91.8 | 70.9 | 54.0 | 14,577 | 43,951 | 2,993.1 |

