import pytest

from adapters import conformance, libpostal_parser
from adapters.registry import ADAPTERS


@pytest.mark.parametrize("name", ["doorplate", "usaddress", "libpostal"])
def test_adapter_conforms(name):
    if name == "libpostal" and not libpostal_parser.available():
        pytest.skip("no libpostal build (tools/libpostal/build.sh, or set LIBPOSTAL_HOME)")
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
