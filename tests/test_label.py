"""The blind labeling tool, on invented cards only."""

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from schema import labels
from tools.label import adjudicate, server, store

TEXT = "12 N Oak St Apt 4, Tampa, FL 33601"


@pytest.fixture
def dirs(tmp_path):
    rounds, logs = tmp_path / "rounds", tmp_path / "logs"
    rounds.mkdir()
    (rounds / "round-1.jsonl").write_text(
        json.dumps({"id": "a1", "text": TEXT})
        + "\n"
        + json.dumps({"id": "a2", "text": "9 Elm Ct, Reno, NV 89501"})
        + "\n"
    )
    return rounds, logs


GOOD = [
    [0, 2, "house_number_value"],
    [3, 4, "street_pre_direction"],
    [5, 8, "street_name"],
    [9, 11, "street_post_type"],
]


def test_keys_cover_every_leaf_label_once():
    keys = store.key_map()
    assert len(set(keys)) == len(keys) and set(keys.values()) == set(store.leaf_labels())
    assert "street" not in keys.values() and "city" in keys.values()
    assert all(labels()[v] for v in keys.values())


@pytest.mark.parametrize(
    "spans",
    [
        [[0, 0, "city"]],
        [[0, 99, "city"]],
        [[0, 2, "street"]],
        [[0, 3, "city"]],
        [[0, 5, "city"], [4, 8, "state"]],
        [[1]],
    ],
)
def test_bad_spans_are_refused_without_quoting_text(spans):
    with pytest.raises(store.CardError) as e:
        store.check_spans(TEXT, spans)
    assert "Tampa" not in str(e.value) and "Oak" not in str(e.value)


def test_save_load_export(dirs):
    rounds, logs = dirs
    cards = {c["id"]: c for c in store.load_round(1, rounds)}
    store.save_card(1, cards["a1"], {"spans": GOOD, "doubtful": True, "ms": 900, "keys": 4}, log_dir=logs)
    store.save_card(1, cards["a1"], {"spans": GOOD[:2]}, log_dir=logs)  # the last save wins
    assert store.load_log(1, logs)["a1"]["spans"] == GOOD[:2]
    with pytest.raises(store.CardError):  # a2 is not labeled
        store.export_round(1, tmp_gold := rounds.parent / "gold", rounds, logs)
    store.save_card(
        1,
        cards["a2"],
        {
            "spans": [[0, 1, "house_number_value"]],
            "alternatives": [{"start": 2, "end": 5, "labels": ["street_name", "building_name"]}],
        },
        log_dir=logs,
    )
    counts = store.export_round(1, tmp_gold, rounds, logs)
    assert counts == {"round": 1, "cards": 2, "doubtful": 0, "with_alternatives": 1, "adjudicated_saves": 0}
    rows = [json.loads(x) for x in (tmp_gold / "round-1.jsonl").read_text().splitlines()]
    assert rows[1]["alternatives"][0]["labels"] == ["building_name", "street_name"]


def test_disagreements_hide_parser_and_respect_coarse_and_alternatives():
    card = {"spans": GOOD, "alternatives": [{"start": 9, "end": 11, "labels": ["street_name"]}]}
    parser = [
        (0, 2, "house_number_value"),
        (3, 11, "street"),
        (9, 11, "street_name"),
        (12, 16, "unit_value"),
        (3, 4, "street_name"),
    ]
    got = adjudicate.disagreements(card, parser)
    assert got == [{"start": 12, "end": 16, "label": "unit_value"}, {"start": 3, "end": 4, "label": "street_name"}]
    assert all(set(q) == {"start", "end", "label"} for q in got)


def test_labeling_modules_never_import_parsers():
    import ast
    from pathlib import Path

    for mod in (store, server):
        tree = ast.parse(Path(mod.__file__).read_text())
        names = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        names += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        assert not [n for n in names if n.split(".")[0] in ("adapters", "doorplate", "usaddress")]


def test_http_round_trip(dirs):
    rounds, logs = dirs
    app = server.App("label", [1], logs, rounds)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(app))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        cards = json.load(urllib.request.urlopen(base + "/api/cards"))
        assert [c["labeled"] for c in cards] == [False, False] and "spans" not in cards[0]
        body = json.dumps({"round": 1, "id": "a1", "spans": GOOD}).encode()
        assert json.load(urllib.request.urlopen(urllib.request.Request(base + "/api/save", body)))["ok"]
        assert json.load(urllib.request.urlopen(base + "/api/cards"))[0]["spans"] == GOOD
        bad = urllib.request.Request(
            base + "/api/save", json.dumps({"round": 1, "id": "a1", "spans": [[0, 99, "city"]]}).encode()
        )
        with pytest.raises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(bad)
        assert e.value.code == 400
        assert b"<canvas" not in urllib.request.urlopen(base + "/").read()
    finally:
        srv.shutdown()


def test_common_labels_get_the_first_keys():
    keys = store.key_map()
    assert keys["1"] == "house_number_value" and keys["0"] == "postal_code"
