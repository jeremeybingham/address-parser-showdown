import pytest

from adapters import conformance, libpostal_parser, rust_worker
from adapters.registry import ADAPTERS

RUST = {"us_address_parser", "addrust", "address_parser"}


@pytest.mark.parametrize(
    "name", ["doorplate", "usaddress", "libpostal", "us_address_parser", "addrust", "address_parser"]
)
def test_adapter_conforms(name):
    if name == "libpostal" and not libpostal_parser.available():
        pytest.skip("no libpostal build (tools/libpostal/build.sh, or set LIBPOSTAL_HOME)")
    if name in RUST and not rust_worker.available():
        pytest.skip("no Rust worker build (cargo build --release --locked in tools/rust-parsers)")
    adapter = ADAPTERS[name]()
    try:
        assert conformance.check(adapter) == []
    finally:
        if hasattr(adapter, "close"):
            adapter.close()


def test_conformance_strings_are_invented_shape():
    cases = conformance.load_strings()
    assert len(cases) >= 36
    assert {k for k, _ in cases} == {"cover", "wellformed"}


def test_us_address_parser_places_direction_and_drops_unfindable_values():
    from adapters.us_address_parser_parser import UsAddressParserAdapter

    adapter = UsAddressParserAdapter()
    spans = adapter._spans(
        "100 Main Street NW",
        [("street_no", "100"), ("street_name", "MAIN"), ("street_type", "ST"), ("direction", "NW")],
    )
    assert [(s.label, s.start, s.end) for s in spans] == [
        ("street_no", 0, 3),
        ("street_name", 4, 8),
        ("direction_post", 16, 18),
    ]  # "ST" is not in the text (it says "Street"), so the type is dropped
    assert adapter._spans("N 100", [("direction", "N")])[0].label == "direction"  # no street name to compare with


def test_address_parser_joins_zip_and_plus4():
    from adapters.address_parser_parser import AddressParserAdapter

    spans = AddressParserAdapter._spans("5 Elm St 12345-6789", [("number", "5"), ("zip", "12345"), ("plus4", "6789")])
    assert [(s.label, s.start, s.end) for s in spans] == [("number", 0, 1), ("zip", 9, 19)]
    apart = AddressParserAdapter._spans("5 Elm St 12345 Box 6789", [("zip", "12345"), ("plus4", "6789")])
    assert [s.label for s in apart] == ["zip", "plus4"]


def test_addrust_drops_rewritten_values_and_keeps_text_order():
    from adapters.rust_worker import place_fields

    spans = place_fields("9 Oak Street", [("suffix", "STREET"), ("street_number", "9"), ("street_name", "OAK")])
    assert [(s.label, s.start, s.end) for s in spans] == [
        ("street_number", 0, 1),
        ("street_name", 2, 5),
        ("suffix", 6, 12),
    ]
