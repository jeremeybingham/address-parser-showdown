"""Shipped gold from private gold: invented values, same length, labels unchanged (invented cards only)."""

import json

from tools.golden import derive

TEXT = "4521 W Quill Ridge Rd Apt 12B, Saltmarsh, OH 44101"  # invented
SPANS = [
    [0, 4, "house_number_value"],
    [5, 6, "street_pre_direction"],
    [7, 18, "street_name"],
    [19, 21, "street_post_type"],
    [22, 25, "unit_type"],
    [26, 29, "unit_value"],
    [31, 40, "city"],
    [42, 44, "state"],
    [45, 50, "postal_code"],
]
CARD = {"id": "x1", "text": TEXT, "spans": SPANS, "alternatives": [], "doubtful": False, "flag": None}


def test_private_values_replaced_and_spans_still_fit():
    new = derive.derive_card(CARD)
    assert len(new) == len(TEXT)
    part = {lab: (TEXT[s:e], new[s:e]) for s, e, lab in SPANS}
    assert part["house_number_value"][1] != "4521" and part["house_number_value"][1].isdigit()
    assert "Quill" not in new and "Ridge" not in new and part["street_name"][1].istitle()
    for lab in ("street_pre_direction", "street_post_type", "unit_type", "city", "state", "postal_code"):
        assert part[lab][0] == part[lab][1]
    assert part["unit_value"][1].endswith("B") and part["unit_value"][1][:2].isdigit()
    assert not derive.leaks(CARD, new)
    assert derive.derive_card(CARD) == new  # deterministic
    assert derive.derive_card(CARD, salt=1) != new


def test_ordinals_stay_ordinals():
    text = "77 E 21st St, Plainview, KS 67001"
    card = {**CARD, "text": text, "spans": [[0, 2, "house_number_value"], [5, 9, "street_name"]]}
    new = derive.derive_card(card)
    n = int(new[5:7])
    assert new[7:9] == derive.ordinal(n)


def test_unlabeled_real_word_is_a_leak_and_non_address_is_replaced():
    text = "Brambleton Quill 12"
    card = {**CARD, "text": text, "spans": [[11, 16, "street_name"]], "flag": None}
    assert derive.leaks(card, derive.derive_card(card)) == {"brambleton"}
    na = {**card, "spans": [], "flag": "non_address"}
    assert not derive.leaks(na, derive.derive_card(na))


def test_derive_round_ships_templates_as_is_and_holds_leaks(tmp_path):
    gold = tmp_path / "gold"
    gold.mkdir()
    leak = {**CARD, "id": "x3", "text": "Brambleton 12", "spans": [[11, 13, "house_number_value"]]}
    cards = [CARD, {**CARD, "id": "x2"}, leak]
    (gold / "round-1.jsonl").write_text("".join(json.dumps(c) + "\n" for c in cards))
    prov = {"x1": {"stratum": "public"}, "x2": {"stratum": "template"}, "x3": {"stratum": "clean"}}
    res = derive.derive_round(1, set(), gold, tmp_path / "out", tmp_path / "review", prov)
    assert res["shipped"] == 2 and res["held"] == {"real-word": 1} and res["held_ids"] == ["x3"]
    out = [json.loads(x) for x in (tmp_path / "out/round-1.jsonl").read_text().splitlines()]
    assert out[0]["text"] != TEXT and out[0]["spans"] == SPANS and out[1]["text"] == TEXT
