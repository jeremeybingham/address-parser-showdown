"""The adjudication-direction count, the highway alternative rule and the breakdown helpers, on invented cards."""

import json

from tools.golden.highway_alt import highway_alternatives
from tools.label import direction

T = "7 US Hwy 50, Zed, ZZ 00001"
HWY = [[0, 1, "house_number_value"], [2, 8, "route_type"], [9, 11, "route_value"], [13, 16, "city"]]


def test_highway_gets_the_street_reading():
    assert highway_alternatives({"text": T, "spans": HWY, "alternatives": []}) == [
        {"start": 2, "end": 11, "labels": ["street_name"]}
    ]


def test_rural_contract_military_and_boxed_routes_do_not():
    t = "RR 2 Box 9, Zed, ZZ 00001"
    boxed = [[0, 2, "route_type"], [3, 4, "route_value"], [5, 8, "route_box_type"], [9, 10, "route_box_value"]]
    assert highway_alternatives({"text": t, "spans": boxed, "alternatives": []}) == []
    for word in ("HC", "PSC", "Star", "R.R.", "Rural"):
        t2 = f"{word} 4, Zed"
        spans = [[0, len(word), "route_type"], [len(word) + 1, len(word) + 2, "route_value"]]
        assert highway_alternatives({"text": t2, "spans": spans, "alternatives": []}) == [], word


def test_an_existing_alternative_is_not_added_twice():
    card = {"text": T, "spans": HWY, "alternatives": [{"start": 2, "end": 11, "labels": ["street_name"]}]}
    assert highway_alternatives(card) == []


def test_join_words_joins_runs_of_one_label():
    t = "La Grange Park"
    assert direction.join_words(t, [(0, 2, "city"), (3, 9, "city"), (10, 14, "city")]) == [(0, 14, "city")]


def test_direction_counts_toward_and_away(tmp_path):
    t = "5 Elm St, La Grange, ZZ"
    before = [[0, 1, "house_number_value"], [2, 5, "street_name"], [6, 8, "street_post_type"], [10, 12, "city"]]
    after = before[:3] + [[10, 19, "city"]]
    log = tmp_path / "round-1.jsonl"
    rows = [
        {"id": "a", "phase": "label", "spans": before, "alternatives": []},
        {"id": "a", "phase": "adjudicate", "spans": after, "alternatives": []},
        {"id": "a", "phase": "schema", "spans": before, "alternatives": []},  # ignored
    ]
    log.write_text("".join(json.dumps(r) + "\n" for r in rows))
    pairs = direction.before_after(1, tmp_path)
    assert pairs["a"][1]["phase"] == "adjudicate"
    right = [(0, 1, "house_number_value"), (2, 5, "street_name"), (6, 8, "street_post_type"), (10, 19, "city")]
    wrong = right[:3] + [(10, 12, "city")]
    got = direction.tally({"a": t}, pairs, {"p": {"a": right}, "q": {"a": wrong}})
    assert got["gold_changed"] == 1
    assert (got["parsers"]["p"]["toward"], got["parsers"]["p"]["away"]) == (1, 0)
    assert (got["parsers"]["q"]["toward"], got["parsers"]["q"]["away"]) == (0, 1)


def test_mcnemar_exact():
    from tools.report.breakdown import mcnemar_exact

    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(5, 5) == 1.0
    assert abs(mcnemar_exact(0, 6) - 2 / 64) < 1e-12
