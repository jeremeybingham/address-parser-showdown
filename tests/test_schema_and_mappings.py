import pytest

import schema
from adapters.base import Mapping, Span, align


def test_schema_parents_are_coarse_and_scopes_valid():
    labs = schema.labels()
    assert {lab.scope for lab in labs.values()} == {"core", "out_of_scope", "unscored"}
    for lab in labs.values():
        assert lab.parent is None or labs[lab.parent].parent is None
    assert schema.coarse("unit_value") == "unit"
    assert schema.coarse("city") == "city"
    assert schema.fine_parts("street") == [
        "street_pre_direction",
        "street_pre_type",
        "street_name",
        "street_post_type",
        "street_post_direction",
    ]


@pytest.mark.parametrize("name", ["doorplate", "usaddress", "libpostal"])
def test_mapping_targets_exist(name):
    assert Mapping(name).claims <= set(schema.labels())


def test_usaddress_mapping_covers_every_model_label():
    import usaddress

    usaddress.TAGGER.open(usaddress.MODEL_PATH)
    assert set(usaddress.TAGGER.labels()) <= Mapping("usaddress").native_labels


def test_libpostal_mapping_covers_documented_labels():
    documented = [
        "house",
        "category",
        "near",
        "house_number",
        "road",
        "unit",
        "level",
        "staircase",
        "entrance",
        "po_box",
        "postcode",
        "suburb",
        "city_district",
        "city",
        "island",
        "state_district",
        "state",
        "country_region",
        "country",
        "world_region",
    ]
    assert set(documented) == Mapping("libpostal").native_labels


def test_box_labels_follow_the_route_context():
    m = Mapping("usaddress")
    plain = m.to_canonical([Span(0, 6, "USPSBoxType"), Span(7, 11, "USPSBoxID")])
    assert [s.label for s in plain] == ["po_box_type", "po_box_value"]
    route = m.to_canonical(
        [
            Span(0, 2, "USPSBoxGroupType"),
            Span(3, 4, "USPSBoxGroupID"),
            Span(5, 8, "USPSBoxType"),
            Span(9, 11, "USPSBoxID"),
        ]
    )
    assert [s.label for s in route] == [
        "route_type",
        "route_value",
        "route_box_type",
        "route_box_value",
    ]


def test_align_trims_separators_skips_none_and_spans_words():
    text = "12 Main  St., Ames"
    spans = align(text, [("12", "a"), ("Main", "b"), ("St.,", "c"), ("Ames", "d")])
    assert [(text[s.start : s.end], s.label) for s in spans] == [
        ("12", "a"),
        ("Main", "b"),
        ("St.", "c"),
        ("Ames", "d"),
    ]
    joined = align(text, [("main st.", "road")], ignore_case=True)
    assert text[joined[0].start : joined[0].end] == "Main  St."
    assert align(text, [("12", None)]) == []


def test_align_error_does_not_quote_input():
    from adapters.base import AlignmentError

    with pytest.raises(AlignmentError) as e:
        align("secretname 1", [("zzz", "x")])
    assert "secretname" not in str(e.value)
