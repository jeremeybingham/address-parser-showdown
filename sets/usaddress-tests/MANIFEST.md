# usaddress test files: manifest

**Source:** [datamade/usaddress](https://github.com/datamade/usaddress) at commit `aa7699b53a0843fc443f9e87285b88cbd9eaf50a`
(2025-08-07), `measure_performance/test_data/`. **License:** MIT, copyright 2014 The Atlanta Journal Constitution.
**Not shipped here:** `tools/sets/usaddress_tests.py` reads unchanged copies from a directory (`$USADDRESS_TESTS`;
default doorplate's vendored copy) and checks each file by SHA-256 first. The fetch script is not written yet.

## Checksums (SHA-256)

| File | Source SHA-256 |
|---|---|
| `us50_test_tagged.xml` | `e4dbaa8a7e95fd7d099bfe89ef5881c751f4b4a808c739a8bc2493289eb2e957` |
| `labeled.xml` | `2a5f222a4c52c73d9abacb3be21b501972d1bfb48ebe7d8bbb80671ea5e755e5` |
| `synthetic_osm_data.xml` | `8d88c7f334e7dd094e38b37ae19e499c91ebaba51f3e77d3ebccd696e5e1e4b2` |
| `synthetic_clean_osm_data.xml` | `bd1a2c19e48058fbf2f724803703b9137b9e5d3d907db8273f46ebd6796d9143` |
| `simple_address_patterns.xml` | `15568e2b9226ca83b6d6a393eb79139e310c64af1494fe13bd5857a512367074` |
| `multi_word_state_addresses.xml` | `4dd5c864938821a9fb006ae1318f8b390d60c2cdf612d05ab012eb5094d3a7a0` |

Converted `build/sets/usaddress-tests.jsonl.gz`: `c696d0d98f465cc92d2d14898d10b3690b4943c10df9d91e11beb4921a38d52c`.

## Parts

| Part | Records |
|---|---|
| `us50_test_tagged` | 687 |
| `labeled` | 146 |
| `synthetic_osm_data` | 4,122 |
| `synthetic_clean_osm_data` | 4,120 |
| `simple_address_patterns` | 8 |
| `multi_word_state_addresses` | 5 |

9,088 records; none dropped.

**Home set for usaddress, every part.** These are usaddress's own regression tests: its `tests/test_labeling.py` asserts
these labels on every release, and new formats go into both its training and its test data. usaddress scores near
100% on them whether or not a string is in its training files, so they are reported on their own line and
out of every aggregate. Not a blind test of any parser.

## Conversion

Usaddress's XML format (one element per token, named by its label) goes through `adapters/mappings/usaddress.toml`; a
trailing comma is not part of a span. `us50_test_tagged` labels a whole street as `StreetName`, and a `StreetNamePreModifier`
token is the coarse `street` label: those are scored on the coarse track. `unparseable.csv` (no labels) is not part of
the set. Overlap with usaddress's training files is doorplate's `in_training.txt` (6,677 strings) and is not applied here.

## Adapter runs

All three adapters ran on every record (`build/predictions/usaddress-tests/`). One error, libpostal on `labeled-00027` (a
multi-line string with an em dash in the ZIP+4: its tokens cannot be placed back in the string); it is recorded as an error
and scored as no output.
