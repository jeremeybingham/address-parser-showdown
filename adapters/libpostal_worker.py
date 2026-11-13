"""Runs inside the libpostal virtualenv (`python -I`): reads JSON lines, answers JSON lines.

In:  {"strings": ["..."]}        Out: {"results": [[["token", "label"], ...], ...]}
Kept apart so that this project's environment does not need the C library.
"""

import json
import sys

from postal.parser import parse_address

for line in sys.stdin:
    request = json.loads(line)
    results = [[list(p) for p in parse_address(s)] for s in request["strings"]]
    sys.stdout.write(json.dumps({"results": results}) + "\n")
    sys.stdout.flush()
