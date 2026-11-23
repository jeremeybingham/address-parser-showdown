"""Render report/REPORT.md as report/REPORT.pdf, with charts drawn from the report's own tables.

    uv run --group report python -m tools.report.pdf [--md report/REPORT.md] [--out report/REPORT.pdf]

The charts read their numbers from the tables in REPORT.md, so the PDF and the markdown can never disagree, and no
figure is typed by hand. Chromium prints the page: the Playwright-managed build is found under ~/.cache/ms-playwright
(set CHROMIUM to point at another binary).
"""

from __future__ import annotations

import argparse
import html
import io
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO_URL = "https://github.com/jeremeybingham/address-parser-showdown/blob/main/"
PARSERS = ["doorplate", "usaddress", "libpostal"]

# Categorical slots 1-3 of the dataviz reference palette (validated all-pairs, light surface #fcfcfb). The third
# slot is under 3:1 contrast, so every chart labels its values and every chart sits next to its table.
COLOR = {"doorplate": "#2a78d6", "usaddress": "#eb6834", "libpostal": "#1baf7a"}
MARKER = {"doorplate": "o", "usaddress": "s", "libpostal": "D"}
INK, INK2, MUTED, RULE, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#e2e1dc", "#ffffff"
FONT = ["Ubuntu Sans", "DejaVu Sans"]
W = 7.0  # chart width in inches = the text width of the page, so chart text prints at its own size

NUM = re.compile(r"^\s*(<?)\s*([\d,]+(?:\.\d+)?)(?:\s*\(([\d.]+) to ([\d.]+)\))?")


# --- reading the markdown -------------------------------------------------------------------------------------------


def clean(cell: str) -> str:
    return re.sub(r"[*`]", "", cell).strip()


def number(cell: str) -> tuple[float, float | None, float | None] | None:
    """`**90.9** (89.8 to 92.0)` -> (90.9, 89.8, 92.0); `1,568` -> (1568.0, None, None); text -> None."""
    m = NUM.match(clean(cell))
    if not m:
        return None
    lo = float(m[3]) if m[3] else None
    hi = float(m[4]) if m[4] else None
    return float(m[2].replace(",", "")), lo, hi


def section(md: str, heading: str) -> str:
    """The text under the first heading that starts with `heading` (e.g. `### 7.2`), up to the next heading of the
    same or a higher level."""
    level = len(heading.split()[0])
    lines = md.splitlines()
    out: list[str] = []
    inside = False
    for line in lines:
        m = re.match(r"^(#+) ", line)
        if inside and m and len(m[1]) <= level:
            break
        if inside:
            out.append(line)
        elif line.startswith(heading):
            inside = True
    if not inside:
        raise KeyError(heading)
    return "\n".join(out)


def tables(text: str) -> list[list[list[str]]]:
    """Every pipe table in `text`, as rows of cells (header row first, the `---` row dropped)."""
    found: list[list[list[str]]] = []
    cur: list[list[str]] = []
    for line in [*text.splitlines(), ""]:
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                cur.append(cells)
        elif cur:
            found.append(cur)
            cur = []
    return found


def columns(table: list[list[str]]) -> dict[str, int]:
    return {clean(h): i for i, h in enumerate(table[0])}


# --- charts ---------------------------------------------------------------------------------------------------------


def _mpl():
    import logging

    import matplotlib

    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    matplotlib.use("svg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": FONT,
            "font.size": 7.5,
            "svg.fonttype": "none",
            "svg.hashsalt": "address-parser-showdown",
            "axes.edgecolor": RULE,
            "axes.labelcolor": INK2,
            "axes.titlesize": 9,
            "axes.titleweight": "bold",
            "axes.titlecolor": INK,
            "axes.titlelocation": "left",
            "xtick.color": INK2,
            "ytick.color": INK,
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
        }
    )
    return plt


def _style(ax, grid_axis: str = "x") -> None:
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    ax.grid(axis=grid_axis, color=RULE, linewidth=0.6)
    ax.set_axisbelow(True)


def _legend(ax) -> None:
    from matplotlib.lines import Line2D

    handles = [
        Line2D([], [], color=COLOR[p], marker=MARKER[p], linestyle="", markersize=6, markeredgecolor=SURFACE, label=p)
        for p in PARSERS
    ]
    ax.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.0, 1.0),
        ncol=3,
        frameon=False,
        handletextpad=0.3,
        borderaxespad=0.2,
    )


def _svg(fig) -> str:
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", pad_inches=0.04, metadata={"Date": None})
    _mpl().close(fig)
    svg = buf.getvalue()
    return svg[svg.index("<svg") :]


def interval_rows(rows: list[tuple[str, dict[str, tuple]]], xlabel: str, xlim=None, height=None) -> str:
    """One band per row, three offset dots with interval whiskers and the value written beside each dot."""
    plt = _mpl()
    n = len(rows)
    fig, ax = plt.subplots(figsize=(W, height or 0.5 * n + 0.6))
    offsets = {"doorplate": -0.24, "usaddress": 0.0, "libpostal": 0.24}
    for i, (_, vals) in enumerate(rows):
        for p in PARSERS:
            v, lo, hi = vals[p]
            y = i + offsets[p]
            if lo is not None:
                ax.plot([lo, hi], [y, y], color=COLOR[p], linewidth=1.6, solid_capstyle="round", zorder=2)
            ax.plot(v, y, marker=MARKER[p], color=COLOR[p], markersize=6, markeredgecolor=SURFACE, mew=1, zorder=3)
            ax.annotate(
                f"{v:.1f}", (hi if hi is not None else v, y), xytext=(5, 0), textcoords="offset points",
                va="center", fontsize=7, color=INK2,
            )  # fmt: skip
        if i:
            ax.axhline(i - 0.5, color=RULE, linewidth=0.6)
    ax.set_yticks(range(n), [r[0] for r in rows])
    ax.set_ylim(n - 0.5, -0.5)
    if xlim:
        ax.set_xlim(*xlim)
    ax.set_xlabel(xlabel)
    _style(ax)
    _legend(ax)
    fig.tight_layout()
    return _svg(fig)


def fig_score(t: list[list[str]]) -> str:
    plt = _mpl()
    c = columns(t)
    fig, axes = plt.subplots(1, 2, figsize=(W, 1.55))
    for ax, key, title in zip(axes, list(c)[1:3], ["Parser Score", "Field F1 score"], strict=True):
        vals = {clean(r[0]): number(r[c[key]]) for r in t[1:]}
        for i, p in enumerate(PARSERS):
            v, lo, hi = vals[p]
            ax.plot([lo, hi], [i, i], color=COLOR[p], linewidth=1.8, solid_capstyle="round")
            ax.plot(v, i, marker=MARKER[p], color=COLOR[p], markersize=7, markeredgecolor=SURFACE, mew=1)
            ax.annotate(f"{v:.1f}", (hi, i), xytext=(5, 0), textcoords="offset points", va="center", fontsize=7.5)
        ax.set_yticks(range(3), PARSERS)
        ax.set_ylim(2.6, -0.6)
        lo_all = min(vals[p][1] for p in PARSERS)
        hi_all = max(vals[p][2] for p in PARSERS)
        ax.set_xlim(lo_all - 1.5, hi_all + 2.0)
        _style(ax)
        ax.set_title(title + " (95% bootstrap interval)", fontsize=8.5)
    fig.tight_layout(w_pad=2.5)
    return _svg(fig)


def fig_sensitivity(t: list[list[str]]) -> str:
    plt = _mpl()
    c = columns(t)
    rows = [(clean(r[0]), {p: number(r[c[p]])[0] for p in PARSERS}) for r in t[1:]]
    fig, ax = plt.subplots(figsize=(W, 0.3 * len(rows) + 0.9))
    for i, (_, vals) in enumerate(rows):
        ax.plot([min(vals.values()), max(vals.values())], [i, i], color=RULE, linewidth=2.2, zorder=1)
        for p in PARSERS:
            ax.plot(vals[p], i, marker=MARKER[p], color=COLOR[p], markersize=6, markeredgecolor=SURFACE, mew=1)
        ax.annotate(
            f"{vals['doorplate']:.1f}", (vals["doorplate"], i), xytext=(6, 0), textcoords="offset points",
            va="center", fontsize=7, color=INK2,
        )  # fmt: skip
        ax.annotate(
            f"{vals['libpostal']:.1f}", (vals["libpostal"], i), xytext=(-6, 0), textcoords="offset points",
            va="center", ha="right", fontsize=7, color=INK2,
        )  # fmt: skip
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xlim(72, 100)
    ax.set_xlabel("Parser Score")
    _style(ax)
    _legend(ax)
    fig.tight_layout()
    return _svg(fig)


def fig_parts(t: list[list[str]]) -> str:
    c = columns(t)
    rows = []
    for r in t[1:]:
        name = clean(r[0])
        if name.lower().startswith("reported apart"):
            break
        label = f"{name}  (n = {clean(r[c['Records']])})"
        rows.append((label, {p: number(r[c[p]]) for p in PARSERS}))
    return interval_rows(rows, "% of records right (95% Wilson interval)", xlim=(40, 103))


def fig_stratum(t: list[list[str]]) -> str:
    c = columns(t)
    rows = [(f"{clean(r[0])}  (n = {clean(r[c['Records']])})", {p: number(r[c[p]]) for p in PARSERS}) for r in t[1:]]
    return interval_rows(rows, "% of records right (95% Wilson interval)", xlim=(40, 103))


def fig_shapes(differ: list[list[str]], fail: list[list[str]]) -> str:
    plt = _mpl()
    rows = []
    for t, group in ((differ, "differ"), (fail, "fail")):
        c = columns(t)
        for r in t[1:]:
            name = re.sub(r"\s*\(in normal\)", "", clean(r[0]))
            rows.append((f"{name} ({clean(r[c['Records']])})", {p: number(r[c[p]])[0] for p in PARSERS}, group))
    n = len(rows)
    fig, ax = plt.subplots(figsize=(W, 0.25 * n + 0.8))
    for i, (_, vals, _) in enumerate(rows):
        ax.plot([min(vals.values()), max(vals.values())], [i, i], color=RULE, linewidth=2.2, zorder=1)
        for p, dy in zip(PARSERS, (-0.17, 0.0, 0.17), strict=True):  # offset so equal values stay visible
            ax.plot(vals[p], i + dy, marker=MARKER[p], color=COLOR[p], markersize=5.5, markeredgecolor=SURFACE,
                    mew=0.8, zorder=3)  # fmt: skip
    split = sum(1 for r in rows if r[2] == "differ")
    ax.axhline(split - 0.5, color=INK2, linewidth=0.8, linestyle=(0, (3, 2)))
    ax.annotate("where all three fail", (100, split - 0.45), fontsize=7, color=INK2, ha="right", va="top",
                style="italic")  # fmt: skip
    ax.set_yticks(range(n), [r[0] for r in rows])
    ax.set_ylim(n - 0.5, -0.5)
    ax.set_xlim(-2, 101)
    ax.set_xlabel("% of records right, all tiers (records in each class in brackets)")
    _style(ax)
    _legend(ax)
    fig.tight_layout()
    return _svg(fig)


def dodge(ys: list[float], gap: float) -> list[float]:
    """Label positions for sorted values `ys`, pushed apart to at least `gap` and centred on the values."""
    out = list(ys)
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1] + gap)
    shift = (sum(out) - sum(ys)) / len(ys)
    return [y - shift for y in out]


def fig_nightmare(t: list[list[str]]) -> str:
    plt = _mpl()
    c = columns(t)
    vals = {clean(r[0]): {p: number(r[c[p]])[0] for p in PARSERS} for r in t[1:]}
    variants = list(vals)
    fig, ax = plt.subplots(figsize=(3.8, 2.3))
    gap = (max(max(v.values()) for v in vals.values()) - min(min(v.values()) for v in vals.values())) * 0.09
    for side, variant in enumerate(variants):
        ys = {p: vals[variant][p] for p in PARSERS}
        for p, y in zip(sorted(PARSERS, key=ys.get), dodge(sorted(ys.values()), gap), strict=True):
            text = f"{p} {ys[p]:.1f}" if side else f"{ys[p]:.1f}"
            ax.annotate(text, (side, y), xytext=(6 if side else -6, 0), textcoords="offset points", va="center",
                        ha="left" if side else "right", fontsize=7.5)  # fmt: skip
    for p in PARSERS:
        ax.plot([0, 1], [vals[v][p] for v in variants], color=COLOR[p], linewidth=2, marker=MARKER[p], markersize=6,
                markeredgecolor=SURFACE)  # fmt: skip
    ax.set_xticks([0, 1], [f"{v}\n(n = {clean(r[c['Records']])})" for v, r in zip(variants, t[1:], strict=True)])
    ax.set_xlim(-0.35, 1.7)
    ax.set_ylabel("% of records right")
    _style(ax, grid_axis="y")
    ax.spines["bottom"].set_visible(False)
    ax.set_title("nightmare: covered against adjacent forms", fontsize=8.5)
    fig.tight_layout()
    return _svg(fig)


def fig_speed(t: list[list[str]]) -> str:
    plt = _mpl()
    c = columns(t)
    rows = {clean(r[0]): {p: number(r[c[p]])[0] for p in PARSERS} for r in t[1:]}

    def pick(prefix: str) -> dict[str, float]:
        return next(v for k, v in rows.items() if k.startswith(prefix))

    panels = [
        ("Strings per second, one process", pick("Strings per second, one"), False, "{:,.0f}"),
        ("Memory after loading (MB, log scale)", pick("Memory after loading"), True, "{:,.0f}"),
        ("Install size (MB, log scale)", pick("Install size"), True, "{:,.1f}"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(W, 1.7))
    for ax, (title, vals, log, fmt) in zip(axes, panels, strict=True):
        for i, p in enumerate(PARSERS):
            if log:
                ax.plot([1, vals[p]], [i, i], color=COLOR[p], linewidth=1.6)
                ax.plot(vals[p], i, marker=MARKER[p], color=COLOR[p], markersize=6, markeredgecolor=SURFACE)
            else:
                ax.barh(i, vals[p], height=0.55, color=COLOR[p])
            ax.annotate(fmt.format(vals[p]), (vals[p], i), xytext=(5, 0), textcoords="offset points", va="center",
                        fontsize=7)  # fmt: skip
        ax.set_yticks(range(3), PARSERS if ax is axes[0] else [""] * 3)
        ax.set_ylim(2.6, -0.6)
        if log:
            ax.set_xscale("log")
            ax.xaxis.set_major_formatter(lambda x, _: f"{x:,.0f}")
            ax.set_xlim(1, max(vals.values()) * 12)
        else:
            ax.set_xlim(0, max(vals.values()) * 1.35)
            ax.xaxis.set_major_formatter(lambda x, _: f"{x / 1000:.0f}k" if x else "0")
        _style(ax)
        ax.set_title(title, fontsize=8)
    fig.tight_layout(w_pad=1.2)
    return _svg(fig)


PIPELINE = """
<svg viewBox="0 0 660 150" xmlns="http://www.w3.org/2000/svg" role="img" class="diagram"
     aria-label="Sets go through each parser's adapter and mapping file into one schema, and the scorer compares spans">
  <defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="#8a8984"/></marker></defs>
  <g font-family="Ubuntu Sans, DejaVu Sans" font-size="11" fill="#0b0b0b">
    <rect x="2" y="20" width="120" height="110" rx="6" fill="#f4f3ef" stroke="#e2e1dc"/>
    <text x="62" y="40" text-anchor="middle" font-weight="700">Test sets</text>
    <text x="62" y="60" text-anchor="middle" font-size="9.5" fill="#52514e">golden: normal,</text>
    <text x="62" y="73" text-anchor="middle" font-size="9.5" fill="#52514e">hard, nightmare</text>
    <text x="62" y="93" text-anchor="middle" font-size="9.5" fill="#52514e">4 neutral parts</text>
    <text x="62" y="113" text-anchor="middle" font-size="9.5" fill="#52514e">home sets (apart)</text>
    <g font-size="10">
      <rect x="160" y="14" width="118" height="30" rx="5" fill="#fff" stroke="#2a78d6" stroke-width="1.5"/>
      <text x="219" y="33" text-anchor="middle">doorplate</text>
      <rect x="160" y="60" width="118" height="30" rx="5" fill="#fff" stroke="#eb6834" stroke-width="1.5"/>
      <text x="219" y="79" text-anchor="middle">usaddress</text>
      <rect x="160" y="106" width="118" height="30" rx="5" fill="#fff" stroke="#1baf7a" stroke-width="1.5"/>
      <text x="219" y="125" text-anchor="middle">libpostal</text>
    </g>
    <text x="219" y="8" text-anchor="middle" font-size="9" fill="#52514e">adapter: spans in own labels</text>
    <rect x="316" y="20" width="132" height="110" rx="6" fill="#f4f3ef" stroke="#e2e1dc"/>
    <text x="382" y="40" text-anchor="middle" font-weight="700">Neutral schema</text>
    <text x="382" y="60" text-anchor="middle" font-size="9.5" fill="#52514e">one mapping file</text>
    <text x="382" y="73" text-anchor="middle" font-size="9.5" fill="#52514e">per parser</text>
    <text x="382" y="93" text-anchor="middle" font-size="9.5" fill="#52514e">8 coarse fields</text>
    <text x="382" y="113" text-anchor="middle" font-size="9.5" fill="#52514e">2 conventions</text>
    <rect x="486" y="20" width="172" height="110" rx="6" fill="#f4f3ef" stroke="#e2e1dc"/>
    <text x="572" y="40" text-anchor="middle" font-weight="700">Scorer</text>
    <text x="572" y="60" text-anchor="middle" font-size="9.5" fill="#52514e">exact character spans</text>
    <text x="572" y="73" text-anchor="middle" font-size="9.5" fill="#52514e">against the hand gold</text>
    <text x="572" y="93" text-anchor="middle" font-size="9.5" fill="#52514e">record accuracy, field F1</text>
    <text x="572" y="113" text-anchor="middle" font-size="9.5" fill="#52514e">Parser Score (formula v1)</text>
    <g stroke="#8a8984" stroke-width="1.3" fill="none" marker-end="url(#ah)">
      <path d="M122,75 L156,29"/><path d="M122,75 L156,75"/><path d="M122,75 L156,121"/>
      <path d="M278,29 L312,62"/><path d="M278,75 L312,75"/><path d="M278,121 L312,88"/>
      <path d="M448,75 L482,75"/>
    </g>
  </g>
</svg>"""


def figure(svg: str, caption: str, cls: str = "") -> str:
    return f'\n\n<figure class="{cls}">{svg}<figcaption>{caption}</figcaption></figure>\n\n'


# --- assembling the page --------------------------------------------------------------------------------------------


def insert_before_table(md: str, heading: str, index: int, block: str) -> str:
    """Put `block` just before the `index`-th table under `heading`."""
    lines = md.split("\n")
    h = next(i for i, line in enumerate(lines) if line.startswith(heading))
    level = len(heading.split()[0])
    seen = -1
    for i in range(h + 1, len(lines)):
        m = re.match(r"^(#+) ", lines[i])
        if m and len(m[1]) <= level:
            break
        if lines[i].startswith("|") and not lines[i - 1].startswith("|"):
            seen += 1
            if seen == index:
                return "\n".join([*lines[:i], block.strip("\n"), "", *lines[i:]])
    raise KeyError(f"{heading} table {index}")


def with_figures(md: str) -> str:
    """REPORT.md with a figure placed just before the table it draws (Figure 1, the pipeline, after the abstract)."""
    s72 = tables(section(md, "### 7.2"))
    s9 = tables(section(md, "## 9."))
    # (heading, which table under it, chart, caption, figure class); captions hold no figures of their own
    plan = [
        ("### 7.2", 0, fig_score(s72[0]), "The pre-registered headline, with paired bootstrap intervals.", ""),
        ("### 7.2", 1, fig_sensitivity(s72[1]),
         "Parser Score under each sensitivity row; each row moves all three scores, and the order holds.", ""),
        ("### 7.3", 0, fig_parts(tables(section(md, "### 7.3"))[0]),
         "Coarse record accuracy of each part in the Parser Score. The parts reported apart are in the table only.",
         ""),
        ("### 7.5", 0, fig_stratum(tables(section(md, "### 7.5"))[0]),
         "The golden set by stratum. The random public stratum (top row) is the part closest to a random draw of "
         "real address lines.", ""),
        ("## 8.", 0, fig_speed(tables(section(md, "## 8."))[0]),
         "Speed and cost. Memory and install size use a log scale.", ""),
        ("## 9.", 0, fig_shapes(s9[0], s9[1]),
         "Coarse record accuracy by shape class, all tiers. Each row spans the lowest to the highest of the three; "
         "classes where all three do well are left out.", ""),
        ("## 9.", 2, fig_nightmare(s9[2]), "The covered and adjacent forms of the nightmare tier.", "small"),
    ]  # fmt: skip
    for n, (heading, index, svg, caption, cls) in reversed(list(enumerate(plan, start=2))):
        md = insert_before_table(md, heading, index, figure(svg, f"Figure {n}. {caption}", cls))
    pipeline = figure(PIPELINE, "Figure 1. How a record is scored: every parser goes through its own adapter and "
                      "mapping file into one schema, and the scorer compares character spans.")  # fmt: skip
    return md.replace("\n## 2. ", pipeline + "\n## 2. ", 1)


def links(html_text: str) -> str:
    def fix(m: re.Match) -> str:
        href = m[1]
        if re.match(r"^[a-z]+:|^#", href):
            return m[0]
        from urllib.parse import urljoin

        return f'href="{urljoin(REPO_URL + "report/", href)}"'

    return re.sub(r'href="([^"]+)"', fix, html_text)


def numeric_cells(html_text: str) -> str:
    return re.sub(r"<td>(\s*(?:<strong>)?[<\d][\d,.]*[^<]*?(?:</strong>)?[^<]*)</td>",
                  lambda m: f'<td class="num">{m[1]}</td>' if NUM.match(re.sub("<[^>]+>", "", m[1])) else m[0],
                  html_text)  # fmt: skip


def run_date(md: str) -> str:
    """The date of the pinned run the report is written from: the first `runs/DATE/` it names."""
    m = re.search(r"runs/(\d{4}-\d{2}-\d{2})/", md)
    if not m:
        raise SystemExit("REPORT.md names no runs/DATE/ folder")
    return m[1]


def cover(md: str) -> tuple[str, str]:
    title = md.splitlines()[0].lstrip("# ").strip()
    t = tables(section(md, "### 7.2"))[0]
    strat = tables(section(md, "### 7.5"))[0]
    c, cs = columns(t), columns(strat)
    tiles = []
    for p in PARSERS:
        row = next(r for r in t[1:] if clean(r[0]) == p)
        v, lo, hi = number(row[c["Parser Score (95% interval)"]])
        sv = number(strat[1][cs[p]])[0]
        tiles.append(
            f'<div class="tile" style="border-top-color:{COLOR[p]}"><div class="tile-name">{p}</div>'
            f'<div class="tile-value">{v:.1f}</div><div class="tile-sub">Parser Score, 95% interval {lo:.1f} to '
            f'{hi:.1f}</div><div class="tile-sub">random public stratum {sv:.1f}</div></div>'
        )
    return title, "".join(tiles)


CSS = """
@page { size: Letter; margin: 0.7in 0.75in 0.75in 0.75in; }
:root { --ink:#0b0b0b; --ink2:#52514e; --muted:#8a8984; --rule:#e2e1dc; --tint:#f4f3ef; --accent:#2a78d6; }
html { color-scheme: light; }
body { background:#fff; color:var(--ink); font-family:"Ubuntu Sans","DejaVu Sans",sans-serif; font-size:9.6pt;
       line-height:1.45; margin:0; }
code, pre { font-family:"Ubuntu Sans Mono","DejaVu Sans Mono",monospace; font-size:0.92em; }
code { background:var(--tint); padding:0 3px; border-radius:3px; }
pre { background:var(--tint); padding:8px 10px; border-radius:5px; white-space:pre-wrap; break-inside:avoid; }
pre code { background:none; padding:0; }
a { color:var(--accent); text-decoration:none; }
h2 { font-size:14pt; margin:22pt 0 6pt; padding-bottom:3pt; border-bottom:1.5px solid var(--ink); break-after:avoid; }
h3 { font-size:11pt; margin:14pt 0 4pt; break-after:avoid; }
p, li { orphans:3; widows:3; }
ul, ol { padding-left:18pt; }
table { border-collapse:collapse; width:100%; margin:6pt 0 10pt; font-size:8.2pt; line-height:1.3; }
thead { display:table-header-group; }
tr { break-inside:avoid; }
th { text-align:left; font-weight:700; border-bottom:1.2px solid var(--ink); padding:3pt 5pt; vertical-align:bottom; }
td { border-bottom:0.6px solid var(--rule); padding:2.5pt 5pt; vertical-align:top; }
td.num { white-space:nowrap; font-variant-numeric:tabular-nums; }
tbody tr:nth-child(even) td { background:#fafaf8; }
figure { margin:10pt 0 12pt; break-inside:avoid; }
figure svg { width:100%; height:auto; display:block; }
figure.small svg { width:54%; margin:0 auto; }
figcaption { font-size:8.2pt; color:var(--ink2); margin-top:4pt; }
.cover { height:9.3in; display:flex; flex-direction:column; break-after:page; }
.kicker { font-size:9pt; letter-spacing:0.12em; text-transform:uppercase; color:var(--ink2); margin-top:0.6in; }
.cover h1 { font-size:27pt; line-height:1.15; margin:10pt 0 14pt; font-weight:700; }
.cover .meta { color:var(--ink2); font-size:10pt; }
.tiles { display:flex; gap:14pt; margin:26pt 0 16pt; }
.tile { flex:1; border-top:4px solid; background:var(--tint); padding:10pt 12pt 12pt; border-radius:0 0 6px 6px; }
.tile-name { font-weight:700; font-size:10.5pt; }
.tile-value { font-size:30pt; font-weight:700; line-height:1.1; margin:4pt 0; font-variant-numeric:tabular-nums; }
.tile-sub { font-size:8pt; color:var(--ink2); }
.cover .note { font-size:9pt; color:var(--ink2); border-left:3px solid var(--rule); padding-left:10pt; }
.cover .foot { margin-top:auto; font-size:8.5pt; color:var(--muted); }
.toc { margin-top:22pt; }
.toc-head { font-weight:700; font-size:10pt; border-bottom:1.2px solid var(--ink); padding-bottom:3pt;
            margin-bottom:6pt; }
.toc > ol { list-style:none; padding:0; margin:0; columns:2; column-gap:24pt; font-size:9.5pt; line-height:1.65; }
.toc ol ol { list-style:none; font-size:8.5pt; line-height:1.5; padding-left:14pt; margin:0 0 3pt; }
.toc li { break-inside:avoid; }
.intro p:first-child { margin-top:0; }
"""


def build_html(md: str) -> str:
    import markdown

    title, tiles = cover(md)
    lines = md.splitlines()
    first_h2 = next(i for i, line in enumerate(lines) if line.startswith("## "))
    intro_md = "\n".join(lines[1:first_h2]).strip()
    body_md = with_figures("\n".join(lines[first_h2:]))

    conv = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"])
    body = conv.convert(body_md)
    toc = conv.toc
    intro = markdown.markdown(intro_md, extensions=["tables"])

    body, intro = numeric_cells(links(body)), links(intro)
    toc = re.sub(r"<div class=\"toc\">|</div>\s*$", "", toc.strip())
    toc = re.sub(r"<li><a[^>]*>US address parsers[^<]*</a>\s*<ul>(.*)</ul>\s*</li>", r"\1", toc, flags=re.S)
    toc = toc.replace("<ul>", "<ol>").replace("</ul>", "</ol>")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>{CSS}</style></head><body>
<section class="cover">
  <div class="kicker">address-parser-showdown · report</div>
  <h1>{html.escape(title)}</h1>
  <div class="meta">Pinned run {run_date(md)} · every figure reproducible from the committed prediction files</div>
  <div class="tiles">{tiles}</div>
  <div class="note">The Parser Score is coarse record accuracy: half on the golden set's three tiers, half on four
  neutral parts (formula version 1, fixed before the first run). The random public stratum is 829 golden records
  drawn at random from public records.</div>
  <nav class="toc"><div class="toc-head">Contents</div>{toc}</nav>
  <div class="foot">{REPO_URL.removesuffix("blob/main/")}<br>Rendered from report/REPORT.md by tools/report/pdf.py;
  the charts read the report's own tables.</div>
</section>
<div class="intro">{intro}</div>
{body}
</body></html>"""


def chromium() -> str:
    if os.environ.get("CHROMIUM"):
        return os.environ["CHROMIUM"]
    found = sorted(Path.home().glob(".cache/ms-playwright/chromium-*/chrome-linux*/chrome"))
    if not found:
        sys.exit("no Chromium found under ~/.cache/ms-playwright; set CHROMIUM to a Chrome binary")
    return str(found[-1])


def render(page_html: str, out: Path, title: str) -> None:
    from playwright.sync_api import sync_playwright

    footer = (
        '<div style="font-family:Ubuntu Sans,DejaVu Sans,sans-serif;font-size:7.5pt;color:#8a8984;width:100%;'
        'padding:0 0.75in;display:flex;justify-content:space-between">'
        f"<span>{html.escape(title)}</span>"
        '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
    )
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chromium(), args=["--no-sandbox"])
        page = browser.new_page()
        page.set_content(page_html, wait_until="load")
        page.pdf(
            path=str(out), prefer_css_page_size=True, print_background=True, display_header_footer=True,
            header_template="<span></span>", footer_template=footer, tagged=True, outline=True,
        )  # fmt: skip
        browser.close()


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--md", type=Path, default=ROOT / "report" / "REPORT.md")
    ap.add_argument("--out", type=Path, default=ROOT / "report" / "REPORT.pdf")
    ap.add_argument("--html", type=Path, help="also write the HTML page here (for checking the layout)")
    args = ap.parse_args(argv)
    md = args.md.read_text()
    page_html = build_html(md)
    if args.html:
        args.html.write_text(page_html)
    render(page_html, args.out, cover(md)[0].split(":")[0])
    print(f"wrote {args.out} ({args.out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main(sys.argv[1:])
