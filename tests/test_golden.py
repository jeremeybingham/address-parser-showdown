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
    for rd in rounds:
        assert {s: sum(x["stratum"] == s for x in rd) for s in sample.QUOTA} == {
            "public": 100,
            "template": 100,
            "clean": 50,
        }


def test_restore_keeps_its_own_generator_and_drops_duplicates():
    kept = [{"real": "1 Elm Street, Reno, NV 89501"}]
    skipped = [
        {"stratum": "public", "source": "nad", "shape": "as-found", "force": None, "row": (st, "Reno", "NV", "89501")}
        for st in ("1 ELM STREET", "2 Oak Road", "3 Pine Lane")
    ]
    a, drop = sample.restore(skipped, kept, 5, set())
    b, _ = sample.restore(skipped, kept, 5, set())
    assert a == b and len(a) == 2 and all(x["restored"] for x in a)
    assert drop == {"nad:duplicate": 1}
