# libpostal `test_us_parses`: manifest

**Source:** `test/test_parser.c`, function `test_us_parses`, in the pinned libpostal clone (`~/projects/libpostal-senzing/src`,
the Senzing-model build, `$LIBPOSTAL_HOME`). **License:** MIT (libpostal). Read from the clone, not copied;
`tools/sets/libpostal_us.py` parses the C source and checks the file by SHA-256 first.

## Checksums (SHA-256)

- Source `test_parser.c`: `d979b2606ff6928f9ad0026fba2594bd07b06150b4967d6355bdfc9e5b5714f0`
- Converted `build/sets/libpostal-us.jsonl.gz`: `6b6ff35de7b5daca24754313277d0475bea9491437af9158ba9ebc788b0d62cb`

## Parts

| Part | Records | Aggregate |
|---|---|---|
| `us` | 53 | **home set for libpostal**: reported on its own line, out of every aggregate |

53 of 53 cases convert. Gold is libpostal's own labels per component (lowercased), mapped by `adapters/mappings/libpostal.toml`;
each value is found in the string, ignoring case, in column order. libpostal does not split a street, so the fine street
parts are not scored on this set. The same 53 strings are the `source=libpostal` rows of Senzing's file (checked by
`senzing_us.py`, which leaves them out).
