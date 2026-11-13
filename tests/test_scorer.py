"""The scorer on invented records only."""

import pytest

from adapters.base import Mapping
from schema import conventions
from scorer import score, spans, stats

F = score.load_formula()


def rec(text, spans_, **kw):
    return {"id": "x", "text": text, "spans": spans_, **kw}


def one(text, gold, pred, alts=()):
    c = score.Counts()
    score.score_record(rec(text, gold, alternatives=list(alts)), pred, F, c)
    return c


T = "123 B Elm St, Pell City, AL 35125"
SUFFIX = [
    [0, 3, "house_number_value"],
    [4, 5, "house_number_suffix"],
    [6, 9, "street_name"],
    [10, 12, "street_post_type"],
]
NAME = [[0, 3, "house_number_value"], [4, 9, "street_name"], [10, 12, "street_post_type"]]
TAIL = [[14, 23, "city"], [25, 27, "state"], [28, 33, "postal_code"]]


def test_formula_weights_sum_to_one_and_groups_are_disjoint():
    w = score.part_weights(F)
    assert sum(w.values()) == pytest.approx(1.0)
    assert w[("golden", "normal")] == pytest.approx(0.5 / 3)
    assert w[("geocode-dev", "dev")] == pytest.approx(0.125)
    assert score.role_of(F, "usaddress-tests", "labeled").startswith("home set")


def test_every_listed_convention_is_implemented_and_scored_out_of_scope_labels_are_claimed_by_all():
    assert set(conventions()) == spans.IMPLEMENTED_CONVENTIONS
    claims = [Mapping(p).claims for p in ("doorplate", "libpostal", "usaddress")]
    assert set(F["out_of_scope_scored"]) <= set.intersection(*claims)


def test_letter_after_number_is_one_answer_on_both_tracks():
    for gold, pred in [(SUFFIX, NAME), (NAME, SUFFIX), (SUFFIX, SUFFIX)]:
        c = one(T, gold + TAIL, pred + TAIL)
        assert c.correct == [1] and c.fine_correct == 1


def test_coarse_only_parser_matches_either_reading_on_coarse():
    coarse = [[0, 3, "house_number"], [4, 12, "street"]] + TAIL
    c = one(T, SUFFIX + TAIL, coarse)
    assert c.correct == [1]


def test_hash_before_unit_both_readings():
    t = "9 Oak Rd # 4, Zed, ZZ 00001"
    base = [[0, 1, "house_number_value"], [2, 5, "street_name"], [6, 8, "street_post_type"]]
    tail = [[14, 17, "city"], [19, 21, "state"], [22, 27, "postal_code"]]
    typed = base + [[9, 10, "unit_type"], [11, 12, "unit_value"]] + tail
    bare = base + [[11, 12, "unit_value"]] + tail
    glued = base + [[9, 12, "unit_value"]] + tail
    for g in (typed, bare, glued):
        for p in (typed, bare, glued):
            assert one(t, g, p).correct == [1]


def test_a_wrong_field_fails_the_record_and_an_extra_field_only_hurts_f1():
    wrong = [[0, 3, "house_number_value"], [4, 9, "street_name"]] + TAIL
    assert one(T, NAME + TAIL, wrong).correct == [0]
    t2 = "12 Elm St"
    c = one(t2, [[0, 2, "house_number_value"]], [[0, 2, "house_number_value"], [3, 9, "street_name"]])
    assert c.correct == [1] and c.fp == [1]


def test_alternatives_accept_each_listed_label():
    t = "12 Elm St B"
    gold = [[0, 2, "house_number_value"], [3, 6, "street_name"], [7, 9, "street_post_type"], [10, 11, "unit_value"]]
    alt = [{"start": 10, "end": 11, "labels": ["street_post_direction"]}]
    pred = gold[:3] + [[10, 11, "street_post_direction"]]
    assert one(t, gold, pred).correct == [0]
    assert one(t, gold, pred, alt).correct == [1]


def test_none_alternative_lets_a_span_go_unlabeled():
    t = "12 Elm St 4"
    gold = [[0, 2, "house_number_value"], [3, 6, "street_name"], [7, 9, "street_post_type"], [10, 11, "unit_value"]]
    alt = [{"start": 10, "end": 11, "labels": ["none"]}]
    assert one(t, gold, gold[:3], alt).correct == [1]


def test_unclaimed_and_coarse_gold_leave_the_fine_track():
    gold = [[0, 2, "house_number_value"], [3, 9, "street"]]
    c = one("12 Elm St", gold, gold)
    assert c.correct == [1] and c.fine_skipped == 1 and c.fine_n == 0


def test_flagged_records_go_to_their_own_part():
    assert score.effective_part({"part": "hard", "flag": "non_address"}) == "hard/non_address"
    assert score.effective_part({"part": "hard"}) == "hard"
    assert score.role_of(F, "golden", "hard/ambiguous").startswith("not in the formula")


def test_wilson_and_f1():
    lo, hi = stats.wilson(50, 100)
    assert (lo, hi) == pytest.approx((0.4038, 0.5962), abs=1e-3)
    assert stats.wilson(0, 0) == (0.0, 0.0)
    assert stats.wilson(100, 100)[1] == 1.0
    assert stats.f1(8, 2, 2) == pytest.approx(0.8) and stats.f1(0, 3, 3) == 0.0


def test_aggregate_bootstrap_and_sensitivity_on_a_toy_run():
    def counts(correct):
        c = score.Counts()
        c.correct = correct
        c.tp = list(correct)
        c.fp = [0] * len(correct)
        c.fn = [1 - x for x in correct]
        return c

    parts = [("golden", "normal"), ("golden", "hard"), ("golden", "nightmare"), ("doorplate-suite", "natural"),
             ("doorplate-suite", "hand"), ("senzing-us", "osm"), ("geocode-dev", "dev")]  # fmt: skip
    res = {k: {"a": counts([1] * 10), "b": counts([1] * 5 + [0] * 5)} for k in parts}
    agg, used = score.aggregate(res, F, ["a", "b"])
    assert agg["a"][0] == pytest.approx(100) and agg["b"][0] == pytest.approx(50) and len(used) == 7
    b = score.bootstrap(res, F, ["a", "b"])
    assert b["a"]["score"] == pytest.approx((100.0, 100.0)) and b["b"]["score"][0] < 50 < b["b"]["score"][1]
    sens = score.sensitivity(res, F, ["a", "b"])
    assert sens["equal weights"]["b"] == pytest.approx(50) and "without golden" in sens


def test_how_a_parser_splits_words_is_not_scored_on_the_fine_track():
    t = "9 Pell City Rd, Zed, ZZ 00001"
    whole = [[0, 1, "house_number_value"], [2, 11, "street_name"], [12, 14, "street_post_type"]]
    split = [[0, 1, "house_number_value"], [2, 6, "street_name"], [7, 11, "street_name"], [12, 14, "street_post_type"]]
    assert one(t, whole, split).fine_correct == 1
