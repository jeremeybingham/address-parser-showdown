# schema

The neutral label schema every parser's output is mapped to. Not written yet (step 1).

Planned fields: house number (with prefix and suffix); street as one coarse field plus the fine parts (pre-direction,
pre-type, name, post-type, post-direction); unit (type and value, up to two); PO box; rural or highway route and box;
city; state; postal code. Out-of-scope labels (recipient, building name, country) are scored only where every parser
claims them. The conventions list (accepted alternative readings, each with its source) lives here too.
