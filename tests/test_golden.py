"""The golden-set tooling, on invented data only (no private source is read)."""

import json
import random

from tools.golden import exclusions, sample, templates

PLACES = [("Springfield", "IL", "62704"), ("Tampa", "FL", "33601"), ("Austin", "TX", "78701")]


def test_templates_are_seeded_and_have_a_place():
    a = templates.make(random.Random(5), PLACES, 50)
    assert a == templates.make(random.Random(5), PLACES, 50)
    assert a != templates.make(random.Random(6), PLACES, 50)
    assert len({shape for _, shape, _ in a}) >= 6
    assert all(any(c.upper() in t.upper() for c, _, _ in PLACES) or "typo" in m for t, _, m in a)


def test_exclusion_normalization_hides_nothing():
    banned = {exclusions.norm("123 N. Main St., Springfield, IL 62704")}
    assert exclusions.hit("123 n main st springfield il 62704", banned)
    assert exclusions.hit("123 N Main St, Elsewhere, MO 65000", {exclusions.norm("123 N Main St")})
    assert not exclusions.hit("PO Box 1, Tampa, FL 33601", {exclusions.norm("PO Box 1")})  # too short to count


def test_exclusion_readers(tmp_path):
    (tmp_path / "a.jsonl").write_text(json.dumps({"fields": {"line1": "9 Elm Court", "city": "Reno"}}) + "\n")
    (tmp_path / "b.xml").write_text(
        "<AddressCollection><AddressString><AddressNumber>7</AddressNumber> <StreetName>Oak</StreetName>"
        " <StreetNamePostType>Lane</StreetNamePostType></AddressString></AddressCollection>"
    )
    (tmp_path / "c.txt").write_text("5 B-HOUSENUM\nPine B-STREET\nAvenue B-ROADTYPE\n-END- -X- -X-\n")
    banned, _ = exclusions.load([tmp_path])
    assert exclusions.norm("9 Elm Court, Reno") in banned
    assert exclusions.norm("5 Pine Avenue") in banned


def test_leak_guard_and_deal():
    assert sample.leaked("12 Whitmore Road", "34 Whitmore Road")
    assert not sample.leaked("12 Whitmore Road", "34 Nodi Road")
    recs = [
        {"text": f"{s}{i}", "stratum": s, "source": s, "shape": s, "style": s}
        for s in sample.QUOTA
        for i in range(sample.QUOTA[s])
    ]
    rounds = sample.deal(recs, 1)
    assert [len(r) for r in rounds] == [250] * 6
    assert all(x["idx"] == j for rd in rounds for j, x in enumerate(rd, 1))
    for rd in rounds:
        assert {s: sum(x["stratum"] == s for x in rd) for s in sample.QUOTA} == {
            "public": 100,
            "template": 100,
            "clean": 50,
        }


def test_restore_keeps_its_own_generator_and_drops_duplicates():
    kept = [{"real": "1 Elm Street, Reno, NV 89501"}]
    skipped = [
        {
            "stratum": "public",
            "source": "nad",
            "shape": "as-found",
            "force": None,
            "row": (st, "Reno", "NV", "89501"),
            "raw": None,
        }
        for st in ("1 ELM STREET", "2 Oak Road", "3 Pine Lane")
    ]
    a, drop = sample.restore(skipped, kept, 5, set(), set())
    b, _ = sample.restore(skipped, kept, 5, set(), set())
    assert a == b and len(a) == 2 and all(x["restored"] for x in a)
    assert drop == {"nad:duplicate": 1}


def test_restore_messy_rows_keep_the_sources_own_last_line():
    skipped = [
        {
            "stratum": "public",
            "source": "fmcsa",
            "shape": "as-found",
            "force": None,
            "row": ("9 OAK RD", "Reno", "NV", "89501"),
            "raw": ("RENO", "nv", "89501-1234"),
        }
    ]
    out, _ = sample.restore(skipped, [], 5, set(), set())
    assert out[0]["text"] == "9 OAK RD, RENO, nv 89501-1234" and out[0]["style"] == "as-written"


def test_placeholder_city_and_final_rounds():
    phrases = {"NOT STATED", "UNKNOWN"}
    assert sample.is_placeholder("Not  Stated", phrases) and sample.is_placeholder("unknown", phrases)
    assert not sample.is_placeholder("Stated College", phrases) and not sample.is_placeholder("", phrases)
    rd = [
        {"idx": 1, "text": "t", "city_placeholder": False},
        {"idx": 2, "text": "t", "city_placeholder": True},
        {"idx": 3, "text": "t", "city_placeholder": False},
    ]
    out = sample.final_rounds([rd], [{"idx": 9, "text": "t"}, {"idx": 8, "text": "t"}])
    assert [x["idx"] for x in out[1]] == [1, 3]  # the id of card 2 is not reused
    assert [x["idx"] for x in out[11]] == [1, 2]
    assert sample.round_lines(out, "g")[1].count("g-r1-003") == 1


def test_restore_drops_placeholder_city_rows():
    skipped = [
        {
            "stratum": "public",
            "source": "nad",
            "shape": "as-found",
            "force": None,
            "row": ("1 ELM STREET", c, "NV", "89501"),
            "raw": None,
        }
        for c in ("Not Stated", "Reno")
    ]
    a, drop = sample.restore(skipped, [], 5, set(), {"NOT STATED"})
    assert len(a) == 1 and drop == {"nad:placeholder-city": 1}
