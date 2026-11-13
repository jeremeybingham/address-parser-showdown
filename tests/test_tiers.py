"""Difficulty tiers (issue #14): class table, tagger, mapping check, golden converter. Invented cards only."""

import json

import pytest

from tools.golden import templates, tiers
from tools.label import store
from tools.sets import golden

TEXT = "12 N Oak St Apt 4, Tampa, FL 33601"
STREET = [
    [0, 2, "house_number_value"],
    [3, 4, "street_pre_direction"],
    [5, 8, "street_name"],
    [9, 11, "street_post_type"],
]
UNIT = [[12, 15, "unit_type"], [16, 17, "unit_value"]]
LAST = [[19, 24, "city"], [26, 28, "state"], [29, 34, "postal_code"]]


def test_every_class_has_a_known_tier_and_origin():
    for name, c in tiers.CLASSES.items():
        assert c.tier in tiers.TIERS, name
        assert c.origin in ("base", "doorplate-research", "outside"), name
        assert (c.origin == "base") == (c.tier != "nightmare"), name


def test_nightmare_classes_are_at_most_half_doorplate_research():
    night = [c for c in tiers.CLASSES.values() if c.tier == "nightmare"]
    assert sum(c.origin == "doorplate-research" for c in night) * 2 <= len(night)


def test_every_template_shape_is_in_the_table():
    assert {s[0] for s in templates.SHAPES} <= set(tiers.CLASSES)


def test_class_from_gold_reads_fields_not_parsers():
    assert tiers.class_from_gold(STREET + LAST) == "directional"
    assert tiers.class_from_gold(STREET + UNIT + LAST) == "street-unit"
    assert tiers.class_from_gold([[0, 2, "house_number_value"], [3, 6, "street_name"]]) == "street-plain"
    assert tiers.class_from_gold([[0, 6, "po_box_type"], [7, 9, "po_box_value"]] + LAST) == "po-box"
    assert tiers.class_from_gold(STREET + [[12, 18, "po_box_type"]]) == "box-and-street"
    assert tiers.class_from_gold([[0, 2, "route_type"], [3, 4, "route_value"]]) == "rural-route"
    assert tiers.class_from_gold(STREET + [[12, 18, "building_name"]]) == "named-place"
    assert tiers.class_from_gold(LAST) == "no-street"
    assert tiers.class_from_gold(STREET + UNIT + [[18, 22, "unit_type"], [23, 24, "unit_value"]]) == "two-units"


def test_mapping_check_needs_every_field_in_every_mapping():
    assert tiers.mapping_ok(STREET + UNIT + LAST)
    assert not tiers.mapping_ok([[0, 2, "route_type"]])  # libpostal has no route
    assert not tiers.mapping_ok(STREET + [[12, 18, "recipient"]])  # out of scope
    assert not tiers.mapping_ok([[0, 2, "other"]])


def test_tier_of_moves_normal_up_and_never_down():
    card = {"spans": STREET + UNIT + LAST}
    tmpl = {"id": "x", "shape": "street-unit", "style": "none"}
    assert tiers.tier_of(tmpl, card) == ("normal", "street-unit", False)
    assert tiers.tier_of(tmpl, card | {"doubtful": True}) == ("hard", "street-unit", True)
    assert tiers.tier_of(tmpl, card | {"flag": "ambiguous"}) == ("hard", "street-unit", True)
    assert tiers.tier_of({"id": "x", "shape": "street-unit", "style": "typo"}, card)[0] == "hard"
    assert tiers.tier_of({"id": "x", "shape": "rural-route", "style": "none"}, card)[0] == "hard"
    assert tiers.tier_of({"id": "x", "shape": "grid", "style": "none"}, card)[0] == "nightmare"
    clean = {"id": "x", "shape": "ordinary", "style": "none"}
    plain = {"spans": [[0, 2, "house_number_value"], [3, 6, "street_name"], [7, 9, "street_post_type"]]}
    assert tiers.tier_of(clean, plain) == ("normal", "ordinary", False)
    public = {"id": "x", "shape": "as-found", "style": "mixed-commas"}
    assert tiers.tier_of(public, {"spans": [[0, 2, "route_type"], [3, 4, "route_value"]]}) == (
        "hard",
        "rural-route",
        False,
    )
    with pytest.raises(KeyError):
        tiers.shape_class({"id": "x", "shape": "made-up"}, [])


def test_flag_is_saved_and_exported(tmp_path):
    rounds, logs, gold = tmp_path / "r", tmp_path / "l", tmp_path / "g"
    rounds.mkdir()
    (rounds / "round-1.jsonl").write_text(json.dumps({"id": "a1", "text": "Same as above"}) + "\n")
    card = store.load_round(1, rounds)[0]
    with pytest.raises(store.CardError):
        store.save_card(1, card, {"flag": "maybe"}, log_dir=logs)
    store.save_card(1, card, {"flag": "non_address"}, log_dir=logs)
    counts = store.export_round(1, gold, rounds, logs)
    assert counts["flagged"] == 1
    assert json.loads((gold / "round-1.jsonl").read_text())["flag"] == "non_address"


def test_golden_converter_sets_part_to_the_tier():
    gold = [
        {"id": "a", "text": TEXT, "spans": STREET + UNIT + LAST, "alternatives": [], "doubtful": False, "flag": None},
        {"id": "b", "text": "Same as above", "spans": [], "alternatives": [], "doubtful": False, "flag": "non_address"},
    ]
    prov = {"a": {"id": "a", "shape": "street-unit", "style": "none"}, "b": {"id": "b", "shape": "non-address-hard"}}
    a, b = golden.convert(gold, prov)
    assert (a["part"], a["shape_class"], "flag" in a) == ("normal", "street-unit", False)
    assert (b["part"], b["flag"]) == ("hard", "non_address")
