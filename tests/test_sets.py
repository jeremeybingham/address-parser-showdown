"""Step 4 converters and the prediction runner, on invented strings only."""

import pytest

from adapters.base import Mapping, Span
from adapters.usaddress_parser import UsaddressAdapter
from tools.sets import doorplate_suite
from tools.sets.common import SpanError, check_spans, merge_adjacent, read_jsonl, tokens_to_spans, write_jsonl
from tools.sets.predict import predict


def test_merge_adjacent_joins_words_but_not_across_a_comma():
    text = "12 OAK RIDGE RD, FAIR HAVEN, VT"
    spans = [
        Span(0, 2, "a"),
        Span(3, 6, "s"),
        Span(7, 12, "s"),
        Span(13, 15, "t"),
        Span(17, 21, "c"),
        Span(22, 27, "c"),
    ]
    assert merge_adjacent(text, spans) == [Span(0, 2, "a"), Span(3, 12, "s"), Span(13, 15, "t"), Span(17, 27, "c")]
    assert merge_adjacent("A, B", [Span(0, 1, "c"), Span(3, 4, "c")]) == [Span(0, 1, "c"), Span(3, 4, "c")]


def test_tokens_to_spans_maps_names_and_keeps_coarse_labels():
    text = "41 OLD MILL ROAD, NEW TOWNE, ZZ 00001"
    tokens = [
        ("41", "AddressNumber"), ("OLD", "StreetNamePreModifier"), ("MILL", "StreetName"),
        ("ROAD,", "StreetNamePostType"), ("NEW", "PlaceName"), ("TOWNE,", "PlaceName"), ("ZZ", "StateName"),
        ("00001", "ZipCode"),
    ]  # fmt: skip
    spans = tokens_to_spans(text, tokens, Mapping("usaddress"))
    assert [(text[s:e], lab) for s, e, lab in spans] == [
        ("41", "house_number_value"), ("OLD", "street"), ("MILL", "street_name"), ("ROAD", "street_post_type"),
        ("NEW TOWNE", "city"), ("ZZ", "state"), ("00001", "postal_code"),
    ]  # fmt: skip


def test_check_spans_refuses_bad_spans():
    with pytest.raises(SpanError):
        check_spans("AB CD", [[0, 3, "city"]])  # ends on a space
    with pytest.raises(SpanError):
        check_spans("AB CD", [[0, 2, "city"], [1, 5, "state"]])
    with pytest.raises(SpanError):
        check_spans("AB", [[0, 2, "nonsense"]])


def test_write_jsonl_repeats_its_bytes(tmp_path):
    rows = [{"id": "x1", "text": "1 A ST", "spans": [], "part": "p"}]
    a, b = tmp_path / "a.jsonl.gz", tmp_path / "b.jsonl.gz"
    write_jsonl(a, rows)
    write_jsonl(b, rows)
    assert a.read_bytes() == b.read_bytes()
    assert list(read_jsonl(a)) == rows


def test_doorplate_suite_convert(tmp_path):
    src = tmp_path / "compare.jsonl.gz"
    row = {
        "id": "v1-x", "input": "9 ELM CT, SOMEWHERE, ZZ 00002", "stratum": "hand", "source": "hand", "type": "street",
        "style": "hand", "mods": [], "tags": [], "state": "ZZ",
        "tokens": [["9", "AddressNumber"], ["ELM", "StreetName"], ["CT,", "StreetNamePostType"],
                   ["SOMEWHERE,", "PlaceName"], ["ZZ", "StateName"], ["00002", "ZipCode"]],
    }  # fmt: skip
    bad = dict(row, id="v1-y", tokens=[["NOPE", "StreetName"]])
    write_jsonl(src, [row, bad])
    records, problems = doorplate_suite.convert(src)
    assert [r["id"] for r in records] == ["v1-x"] and problems == {"AlignmentError": 1}
    assert records[0]["part"] == "hand" and records[0]["spans"][0] == [0, 1, "house_number_value"]


def test_predict_writes_native_and_canonical_spans():
    records = [{"id": "r1", "text": "123 Main St, Springfield, IL 62701"}, {"id": "r2", "text": ""}]
    preds = list(predict(UsaddressAdapter(), records))
    assert [p["id"] for p in preds] == ["r1", "r2"]
    first = preds[0]
    assert first["error"] is None and len(first["native"]) == len(first["spans"])
    assert ("city" in {lab for _, _, lab in first["spans"]}) and preds[1]["spans"] == []
