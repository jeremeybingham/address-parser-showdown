"""The speed script's pieces, on invented numbers (no parser is run)."""

from tools.bench import speed


def test_summarize_uses_the_median_pass():
    got = speed.summarize([2.0, 1.0, 4.0], 100)
    assert got["median_s"] == 2.0 and got["per_second"] == 50.0
    assert (got["fastest_s"], got["slowest_s"]) == (1.0, 4.0)


def test_render_names_machine_and_every_parser():
    one = {
        "per_second": 10.0,
        "fastest_s": 9.0,
        "slowest_s": 11.0,
        "load_seconds": 0.1,
        "rss_after_load_mb": 5.0,
        "rss_after_parses_mb": 6.0,
    }
    four = {**one, "pss_total_after_load_mb": 20.0}
    res = {
        "machine": "test machine", "reference_profile": "4 CPUs, 8 GB", "strings": 100, "distinct": 10, "reps": 3,
        "parsers": {"a": {"versions": {"a": "1"}, "one": one, "4": four, "install_mb": 1.5, "install_what": "x"}},
    }  # fmt: skip
    md = speed.render(res, 4)
    assert "test machine" in md and "| a |" in md and "1.5 MB" in md
