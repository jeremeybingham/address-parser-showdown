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
    assert counts == {
        "round": 1,
        "cards": 2,
        "doubtful": 0,
        "rough": 0,
        "with_unscored": 0,
        "flagged": 0,
        "revisit_open": 0,
        "late_changes": 0,
        "with_alternatives": 1,
        "adjudicated_saves": 0,
    }
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
        after = json.load(urllib.request.urlopen(base + "/api/cards"))
        assert [c["id"] for c in after] == ["a2", "a1"]  # the undone card is served first, the labeled one after
        assert after[1]["spans"] == GOOD and after[1]["n"] == 1
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


def test_alternative_may_be_none():
    assert store.check_alternatives(TEXT, [{"start": 9, "end": 10, "labels": ["none", "unit_type"]}])[0]["labels"] == [
        "none",
        "unit_type",
    ]


def test_a_save_made_on_other_text_is_stale(dirs, tmp_path):
    rounds, logs = dirs
    legacy = tmp_path / "legacy"
    legacy.mkdir()
    # the anonymized text of a1 differs from the labeled text; a2 is the same in both (a template card)
    (legacy / "round-1.jsonl").write_text(
        json.dumps({"id": "a1", "text": "12 N Zub St Apt 4, Tampa, FL 33601"})
        + "\n"
        + json.dumps({"id": "a2", "text": "9 Elm Ct, Reno, NV 89501"})
        + "\n"
    )
    old = {"phase": "label", "spans": [], "alternatives": [], "doubtful": False, "flag": None, "ms": 1, "keys": 1}
    logs.mkdir()
    (logs / "round-1.jsonl").write_text(json.dumps({"id": "a1", **old}) + "\n" + json.dumps({"id": "a2", **old}) + "\n")
    cards = {c["id"]: c for c in store.gold_cards(1, rounds, logs, legacy)}
    assert cards["a1"]["stale"] and not cards["a1"]["labeled"]  # saved before the stamp, on the anonymized text
    assert cards["a2"]["labeled"] and not cards["a2"]["stale"]
    store.save_card(1, {"id": "a1", "text": TEXT}, {"spans": GOOD}, log_dir=logs)
    cards = {c["id"]: c for c in store.gold_cards(1, rounds, logs, legacy)}
    assert cards["a1"]["labeled"] and cards["a1"]["spans"] == GOOD


def test_requeue_makes_a_card_unlabeled_again(dirs):
    rounds, logs = dirs
    card = store.load_round(1, rounds)[0]
    store.save_card(1, card, {"spans": GOOD}, log_dir=logs)
    assert store.gold_cards(1, rounds, logs)[0]["labeled"]
    store.requeue(1, [card["id"]], log_dir=logs)
    assert not store.gold_cards(1, rounds, logs)[0]["labeled"]
    store.save_card(1, card, {"spans": GOOD}, log_dir=logs)  # and it can be labeled again
    assert store.gold_cards(1, rounds, logs)[0]["labeled"]


def test_lint_flags_typos_without_quoting_text():
    from tools.label import lint

    text = "12 N Elm St, Reno, NV 89501"
    good = [[0, 2, "house_number_value"], [3, 4, "street_pre_direction"], [5, 8, "street_name"],
            [9, 11, "street_post_type"], [13, 17, "city"], [19, 21, "state"], [22, 27, "postal_code"]]  # fmt: skip
    zips = {"89501": {"NV"}}
    assert lint.lint_card({"text": text, "spans": good}, zips) == []
    bad_state = [*good[:5], [13, 17, "city"], [19, 21, "state"], [22, 27, "postal_code"]]
    assert lint.lint_card({"text": text.replace("NV", "NC"), "spans": bad_state}, zips) == ["zip-state"]
    wrong = [s if s[2] != "street_pre_direction" else [3, 4, "street_name"] for s in good]
    assert "duplicate" not in lint.lint_card({"text": text, "spans": wrong}, zips)  # a split street name is fine
    assert lint.lint_card({"text": text, "spans": good[:6]}, zips) == ["uncovered"]
    assert lint.lint_card({"text": text, "spans": good[:6], "flag": "ambiguous"}, zips) == []
    ne = [[0, 2, "house_number_value"], [3, 7, "street_post_direction"]]
    assert "dir-shape" not in lint.lint_card({"text": "12 N.E.", "spans": ne}, zips)


def test_review_mode_serves_queue_with_saved_labels(tmp_path):
    from tools.label.server import App

    rounds, logs = tmp_path / "rounds", tmp_path / "labels"
    rounds.mkdir()
    (rounds / "round-1.jsonl").write_text(json.dumps({"id": "a", "text": "12 Oak"}) + "\n")
    card = {"id": "a", "text": "12 Oak"}
    store.save_card(1, card, {"spans": [[0, 2, "house_number_value"]]}, log_dir=logs)
    logs.mkdir(exist_ok=True)
    (logs / "review-queue.jsonl").write_text(json.dumps({"round": 1, "id": "a", "rules": ["uncovered"]}) + "\n")
    app = App("review", [1], log_dir=logs, rounds_dir=rounds)
    [c] = app.cards_payload()
    assert c["rules"] == ["uncovered"] and c["spans"] == [[0, 2, "house_number_value"]]
    app.save({"round": 1, "id": "a", "spans": [[0, 2, "house_number_value"], [3, 6, "street_name"]]})
    assert store.load_log(1, logs)["a"]["phase"] == "review"


def test_status_sureness_unscored_and_notes_are_saved_but_notes_never_exported(dirs):
    rounds, logs = dirs
    cards = {c["id"]: c for c in store.load_round(1, rounds)}
    payload = {
        "spans": GOOD,
        "unscored": [[12, 17]],  # "Apt 4"
        "flag": "multi_address",
        "rough": True,
        "note": "  look again  ",
        "revisit": True,
    }
    rec = store.save_card(1, cards["a1"], payload, log_dir=logs)
    assert (rec["note"], rec["revisit"], rec["unscored"], rec["rough"]) == ("look again", True, [[12, 17]], True)
    store.save_card(1, cards["a2"], {"flag": "intersection", "spans": [[2, 5, "street_name"]]}, log_dir=logs)
    gold = rounds.parent / "gold"
    counts = store.export_round(1, gold, rounds, logs)
    assert (counts["rough"], counts["with_unscored"], counts["revisit_open"], counts["flagged"]) == (1, 1, 1, 2)
    raw = (gold / "round-1.jsonl").read_text()
    assert "look again" not in raw and '"note"' not in raw and '"revisit"' not in raw
    assert json.loads(raw.splitlines()[0])["unscored"] == [[12, 17]]


@pytest.mark.parametrize(
    "payload",
    [
        {"spans": GOOD, "doubtful": True, "rough": True},
        {"spans": GOOD, "unscored": [[3, 8]]},  # overlaps a span
        {"spans": GOOD, "unscored": [[11, 17]]},  # starts on a space
        {"spans": GOOD, "unscored": [[12, 17], [15, 20]]},
        {"spans": GOOD, "note": "x" * 501},
        {"spans": GOOD, "flag": "two_doors"},
    ],
)
def test_bad_status_payloads_are_refused(dirs, payload):
    rounds, logs = dirs
    card = store.load_round(1, rounds)[0]
    with pytest.raises(store.CardError) as e:
        store.save_card(1, card, payload, log_dir=logs)
    assert "Tampa" not in str(e.value) and "Oak" not in str(e.value)


def test_old_saves_without_the_new_fields_still_load(dirs):
    rounds, logs = dirs
    logs.mkdir()
    old = {"id": "a1", "phase": "label", "spans": GOOD, "alternatives": [], "doubtful": False, "flag": None}
    (logs / "round-1.jsonl").write_text(json.dumps({**old, "th": store.text_hash(TEXT)}) + "\n")
    card = store.gold_cards(1, rounds, logs)[0]
    assert (card["rough"], card["unscored"], card["note"], card["revisit"]) == (False, [], "", False)


def test_late_changes_count_only_marks_changed_after_adjudication_began(dirs):
    rounds, logs = dirs
    cards = {c["id"]: c for c in store.load_round(1, rounds)}
    store.save_card(1, cards["a1"], {"spans": GOOD}, log_dir=logs)
    store.save_card(1, cards["a1"], {"spans": GOOD, "doubtful": True}, phase="review", log_dir=logs)  # still blind
    store.save_card(1, cards["a2"], {"spans": [[0, 1, "house_number_value"]]}, log_dir=logs)
    assert store.late_changes(1, logs) == []
    store.save_card(1, cards["a1"], {"spans": GOOD, "doubtful": True}, phase="adjudicate", log_dir=logs)  # same marks
    store.save_card(1, cards["a2"], {"spans": [[0, 1, "house_number_value"]]}, phase="adjudicate", log_dir=logs)
    assert store.late_changes(1, logs) == []
    store.save_card(1, cards["a2"], {"spans": [[0, 1, "house_number_value"]], "rough": True}, log_dir=logs)
    assert store.late_changes(1, logs) == ["a2"]  # a later save still counts as after the parsers ran


def test_revisit_mode_serves_only_marked_cards(dirs):
    rounds, logs = dirs
    cards = {c["id"]: c for c in store.load_round(1, rounds)}
    store.save_card(1, cards["a1"], {"spans": GOOD}, log_dir=logs)
    store.save_card(1, cards["a2"], {"spans": [[0, 1, "house_number_value"]], "revisit": True}, log_dir=logs)
    app = server.App("revisit", [1], logs, rounds)
    got = app.cards_payload()
    assert [c["id"] for c in got] == ["a2"] and got[0]["round"] == 1
    assert app.save({"round": 1, "id": "a2", "spans": [[0, 1, "house_number_value"]]})["phase"] == "review"


def test_lint_two_doors_and_unscored_text_is_not_uncovered():
    from tools.label import lint

    t = "12 Oak St & 14 Elm Ave"
    two = {
        "text": t,
        "spans": [
            [0, 2, "house_number_value"],
            [3, 6, "street_name"],
            [7, 9, "street_post_type"],
            [12, 14, "house_number_value"],
            [15, 18, "street_name"],
            [19, 22, "street_post_type"],
        ],
    }
    assert "two-doors" in lint.lint_card(two)
    assert lint.lint_card({**two, "flag": "multi_address"}) == []
    words = {
        "text": "12 Oak Hill St",
        "spans": [
            [0, 2, "house_number_value"],
            [3, 6, "street_name"],
            [7, 11, "street_name"],
            [12, 14, "street_post_type"],
        ],
    }
    assert "two-doors" not in lint.lint_card(words)  # one name labeled word by word
    part = {"text": t, "spans": [[0, 2, "house_number_value"], [3, 6, "street_name"], [7, 9, "street_post_type"]]}
    assert "uncovered" in lint.lint_card(part)
    assert "uncovered" not in lint.lint_card({**part, "unscored": [[12, 22]]})
