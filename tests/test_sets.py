"""Step 4 converters and the prediction runner, on invented strings only."""

import pytest

from adapters.base import AlignmentError, Mapping, Span
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


def test_components_to_spans_finds_lowercased_values_in_order():
    from tools.sets.common import components_to_spans

    text = "Acme Co 12 Oak Rd, Fair Haven, VT 00001"
    comps = [("house", "acme co"), ("house_number", "12"), ("road", "oak rd"), ("city", "fair haven"),
             ("state", "vt"), ("postcode", "00001")]  # fmt: skip
    spans = components_to_spans(text, comps, Mapping("libpostal"))
    assert [(text[s:e], lab) for s, e, lab in spans] == [
        ("Acme Co", "building_name"), ("12", "house_number"), ("Oak Rd", "street"), ("Fair Haven", "city"),
        ("VT", "state"), ("00001", "postal_code"),
    ]  # fmt: skip
    with pytest.raises(AlignmentError):
        components_to_spans(text, [("road", "elm st")], Mapping("libpostal"))


def test_libpostal_us_cases_skip_comments_and_check_counts(tmp_path):
    from tools.sets import libpostal_us

    src = tmp_path / "t.c"
    src.write_text(
        "TEST test_us_parses(void) {\n"
        "    CHECK_CALL(test_parse_result_equals(\n"
        "        // a comment between the call and the string\n"
        '        "12 Oak Rd, Fair Haven, VT",\n'
        "        options,\n"
        "        2,\n"
        '        (labeled_component_t){"house_number", "12"},\n'
        '        (labeled_component_t){"road", "oak rd"}\n'
        "    ));\n"
        "}\n"
    )
    assert list(libpostal_us.us_cases(src)) == [
        ("12 Oak Rd, Fair Haven, VT", [("house_number", "12"), ("road", "oak rd")])
    ]


def test_geocode_iob_and_usaddress_xml_readers(tmp_path):
    from tools.sets import geocode_dev, usaddress_tests

    iob = tmp_path / "dev.txt"
    iob.write_text("12 B-HOUSENUM\nOAK B-STREET\nRD B-ROADTYPE\nFAIR B-CITY\nHAVEN I-CITY\n-END- -X- -X- \n\t\n")
    (tokens,) = geocode_dev.read_iob(iob)
    assert tokens[0] == ("12", "AddressNumber") and len(tokens) == 5
    xml = tmp_path / "t.xml"
    xml.write_text(
        "<AddressCollection><AddressString><AddressNumber>12</AddressNumber> "
        "<StreetName>Oak,</StreetName> <PlaceName>Haven</PlaceName></AddressString></AddressCollection>"
    )
    ((text, toks),) = usaddress_tests.read_xml(xml)
    assert text == "12 Oak, Haven" and toks[1] == ("Oak,", "StreetName")
