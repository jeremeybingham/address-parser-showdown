# schema

The neutral label schema every parser's output is mapped to. The labels are in [`schema.toml`](schema.toml) (loaded by
`schema/__init__.py`); the conventions list is [`conventions.toml`](conventions.toml).

## Labels

A **coarse field** is the unit of the headline score; a **fine part** (a label with a `parent`) is scored on the fine
track. A parser that cannot split a field (libpostal's `road`) maps to the coarse label, and its fine label for the fine
track is the coarse label.

| Coarse field | Fine parts |
|---|---|
| `house_number` | `house_number_prefix`, `house_number_value`, `house_number_suffix` |
| `street` | `street_pre_direction`, `street_pre_type`, `street_name`, `street_post_type`, `street_post_direction` |
| `unit` | `unit_type`, `unit_value` (up to two units: a second pair follows the first) |
| `po_box` | `po_box_type`, `po_box_value` (general delivery included) |
| `route` | `route_type`, `route_value`, `route_box_type`, `route_box_value` (rural, highway contract and military routes) |
| `city`, `state`, `postal_code` | none |

**Out of scope** (scored only where every parser claims them): `recipient`, `building_name`, `country`. `other` is where
a parser's label with no home here goes; it is never scored.

## Conventions

Where reasonable readings differ, the gold accepts each reading listed in `conventions.toml` (format in the file's
header; every entry needs a source). The list is fixed before the first scored run (see
[`METHODOLOGY.md`](../METHODOLOGY.md)). It holds two conventions, chosen by the owner on 2026-11-13: a letter after a house number (`123 B ELM ST`: suffix or street name) and `#` before a unit (the `#` is the unit type, or left unlabeled). `EXT` after a street and a compass word that starts a city (`S ELGIN`) were considered and left to the gold.

## Mappings

Each parser's labels map to these in `adapters/mappings/<parser>.toml` (see [`adapters/`](../adapters/README.md)). A
change here means checking every mapping and the conformance test.
