"""The PDF renderer reads its chart numbers from REPORT.md's tables; these check that reading (no browser needed)."""

from tools.report import pdf

MD = """# Title

## 7. Results

### 7.2 Score

Intro.

| Parser | Score (95% interval) |
|---|---|
| doorplate | **90.9** (89.8 to 92.0) |
| usaddress | 84.7 |

| Second | n |
|---|---|
| a | 1,568 |

### 7.3 Next

| x |
|---|
| 1 |
"""


def test_number_reads_value_and_interval():
    assert pdf.number("**90.9** (89.8 to 92.0)") == (90.9, 89.8, 92.0)
    assert pdf.number("1,568") == (1568.0, None, None)
    assert pdf.number("same") is None


def test_tables_stay_inside_their_section():
    found = pdf.tables(pdf.section(MD, "### 7.2"))
    assert [t[0][0] for t in found] == ["Parser", "Second"]
    assert found[0][1] == ["doorplate", "**90.9** (89.8 to 92.0)"]


def test_insert_before_table_picks_the_right_table():
    out = pdf.insert_before_table(MD, "### 7.2", 1, "<figure>F</figure>")
    assert out.index("<figure>F</figure>") < out.index("| Second |")
    assert out.index("<figure>F</figure>") > out.index("| usaddress |")


def test_dodge_keeps_labels_apart():
    ys = pdf.dodge([52.1, 53.0, 61.5], 3.0)
    assert all(b - a >= 3.0 - 1e-9 for a, b in zip(ys, ys[1:], strict=False))


def test_report_tables_have_every_parser():
    md = (pdf.ROOT / "report" / "REPORT.md").read_text()
    head = pdf.columns(pdf.tables(pdf.section(md, "### 7.3"))[0])
    assert set(pdf.PARSERS) <= set(head)


def test_run_date_is_the_first_run_the_report_names():
    md = "# T\n\nWritten from [`runs/2026-11-23/`](../runs/2026-11-23/); replaces `runs/2026-11-16/`.\n"
    assert pdf.run_date(md) == "2026-11-23"
