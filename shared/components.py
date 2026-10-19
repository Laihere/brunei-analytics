"""Page components for case studies (DESIGN.md §5), returned as HTML for Quarto cells.

Each helper returns a RawHTML object (shared/html.py), so a cell that ends with one renders it
as-is. Text arguments are escaped; only `fig` and `df` produce markup of their own.
"""

import re
from html import escape
from pathlib import Path
from typing import Literal

import pandas as pd
import plotly.graph_objects as go
import yaml

from shared.charts import CONFIG, data_table
from shared.context import ContextSource, apa_context_reference
from shared.html import RawHTML as HTML
from shared.provenance import BYLINE, Provenance, apa_reference, apa_year_labels, short_credit

Change = Literal["up-good", "up-bad", "down-good", "down-bad"]
_ARROW = {"up": "▲", "down": "▼"}
_CHANGE_TEXT = {"good": "improvement", "bad": "worsening"}


def stat_tile(
    label: str, value: str, delta: str = "", context: str = "", change: Change | None = None
) -> str:
    """One stat tile, e.g. stat_tile("Food CPI", "+4.1%", "1.3 pts", "vs 2024", "up-bad").

    `change` adds an arrow and a colour to `delta`. The arrow and a visually hidden
    word carry the meaning, so colour is never the only signal.
    """
    line = ""
    if delta:
        if change:
            direction, verdict = change.split("-")
            line = (
                f'<b class="{change}">{_ARROW[direction]} {escape(delta)}'
                f'<span class="visually-hidden"> ({_CHANGE_TEXT[verdict]})</span></b>'
            )
        else:
            line = f"<b>{escape(delta)}</b>"
    if context:
        line += f" {escape(context)}"
    delta_html = f'<div class="delta">{line.strip()}</div>' if line else ""
    return (
        f'<div class="tile"><div class="label">{escape(label)}</div>'
        f'<div class="value">{escape(value)}</div>{delta_html}</div>'
    )


def stat_tiles(*tiles: str) -> HTML:
    """Row of at most 3 stat tiles (Hick's Law, Miller's Law)."""
    if not 1 <= len(tiles) <= 3:
        raise ValueError("Use 1–3 stat tiles (DESIGN.md §4.1).")
    return HTML(f'<section class="tiles" aria-label="Key numbers">{"".join(tiles)}</section>')


def chart_card(
    fig: go.Figure | str,
    title: str,
    subtitle: str,
    alt: str,
    provenance: list[Provenance],
    table: pd.DataFrame,
    height: int = 360,
    mobile_fig: go.Figure | str | None = None,
    mobile_height: int | None = None,
) -> HTML:
    """Chart with its takeaway heading, credit line and table view in one card
    (Common Region, Proximity; policy M1–M3).

    `mobile_fig` is an optional phone layout of the same data (e.g. fewer columns of small
    multiples); CSS shows one or the other at the 720px breakpoint. `fig` may also be a static
    SVG string from shared.svg (treemaps etc.); `height` then doesn't apply, as the SVG keeps
    its own shape.
    """
    if not alt.strip():
        raise ValueError("Charts need a one-sentence text summary for screen readers.")

    def render(f: go.Figure | str, h: int) -> str:
        if isinstance(f, str):
            return f
        # The subtitle carries the measure and unit, so axis titles would only repeat it.
        f.update_layout(height=h, dragmode=False)
        f.update_xaxes(title=None, fixedrange=True)  # every subplot axis: no zoom or pan
        f.update_yaxes(title=None, fixedrange=True)
        return f.to_html(full_html=False, include_plotlyjs=False, config=CONFIG)

    plot = render(fig, height)
    if mobile_fig is not None:
        plot = (
            f'<div class="chart-wide">{plot}</div>'
            f'<div class="chart-narrow">{render(mobile_fig, mobile_height or height)}</div>'
        )
    return HTML(
        '<figure class="chart-card">'
        f'<p class="chart-title">{escape(title)}</p>'
        f'<p class="chart-sub">{escape(subtitle)}</p>'
        f'<div class="chart" role="img" aria-label="{escape(alt)}">{plot}</div>'
        f'<figcaption class="credit">{escape(short_credit(provenance))}</figcaption>'
        "<details><summary>Show data table</summary>"
        # Own scroll box (keyboard-focusable), so wide tables never scroll the chart with them.
        '<div class="table-box" tabindex="0" role="region" '
        f'aria-label="Data table: {escape(title)}">'
        f"{data_table(table)}</div></details>"
        "</figure>"
    )


def method_and_sources(
    provenance: list[Provenance],
    notes: str,
    steps: list[str],
    code_url: str = "",
    context: list[ContextSource] = (),
) -> HTML:
    """Layer 4: method, full attributions and code, collapsed but always present.

    `context` adds news, journal and official sources (policy §7) to the same APA list.
    """
    items = "".join(f"<li>{escape(s)}</li>" for s in steps)
    unique = list(dict.fromkeys(provenance))  # same dataset may back several outputs
    years = apa_year_labels(unique)  # same author and year: 2026a, 2026b…
    refs = [apa_reference(p, html=True, year=years[p]) for p in unique]
    refs += [apa_context_reference(c, html=True) for c in dict.fromkeys(context)]
    refs.sort(key=lambda r: re.sub(r"<[^>]+>", "", r).lower())  # APA: alphabetical
    credits = "".join(f"<li>{r}</li>" for r in refs)
    code = (
        f'<details><summary>Code on GitHub</summary><div><a href="{escape(code_url)}">'
        f"{escape(code_url)}</a></div></details>"
        if code_url
        else ""
    )
    return HTML(
        '<section id="method" class="detail-group" aria-label="Method and sources">'
        f"<details><summary>Method</summary><div><ol>{items}</ol>"
        f"<p><strong>Transformations:</strong> {escape(notes)}</p></div></details>"
        f'<details><summary>References (APA)</summary><div><ul class="references">{credits}</ul>'
        f"<p>Analysis by {escape(BYLINE)} (see "
        '<a href="../about.html#how-ai-was-used">how AI was used</a>). '
        "Not an official publication of the Government of Brunei Darussalam.</p></div></details>"
        f"{code}</section>"
    )


def _front_matter(path: Path) -> dict:
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    return yaml.safe_load(text.split("---", 2)[1]) or {}


# How two case studies connect (front matter `related:`). Only the newer study declares the
# link; the older one shows it automatically, so published pages never need editing for it.
RELATION_LABELS = {
    "follow-up": ("Builds on", "Followed up in"),  # newer data or a deeper look, same question
    "same-source": ("Same source", "Same source"),
    "same-topic": ("Related topic", "Related topic"),
}


def _studies(pages_dir: Path) -> dict[str, tuple[str, dict]]:
    """Case study number → (page stem, front matter)."""
    return {
        str(meta["number"]): (p.stem, meta)
        for p in sorted(pages_dir.glob("*.qmd"))
        if not p.name.startswith("_") and "number" in (meta := _front_matter(p))
    }


def related_links(pages_dir: Path) -> list[tuple[str, str, str, str]]:
    """Every declared link as (from number, to number, kind, why), checked."""
    studies = _studies(pages_dir)
    links = []
    for num, (stem, meta) in studies.items():
        seen = set()
        for r in meta.get("related") or []:
            to, kind, why = str(r.get("study", "")), r.get("kind", ""), r.get("why", "").strip()
            if to not in studies:
                raise ValueError(f"{stem}: related study {to!r} does not exist.")
            if int(to) >= int(num):
                raise ValueError(f"{stem}: only link to earlier studies ({to}); it shows on both.")
            if kind not in RELATION_LABELS:
                raise ValueError(f"{stem}: related kind {kind!r}; use {list(RELATION_LABELS)}.")
            if not why:
                raise ValueError(f"{stem}: say how it relates to {to} ('why').")
            if re.search(r"\b(here|this study)\b", why, re.IGNORECASE):
                raise ValueError(f"{stem}: 'why' shows on both pages; name studies by number.")
            if to in seen:
                raise ValueError(f"{stem}: {to} is listed twice.")
            seen.add(to)
            links.append((num, to, kind, why))
    return links


def related_studies(current: str, pages_dir: Path) -> HTML:
    """ "Related case studies" box after the conclusion: earlier studies this one links to, and
    later ones that link back (nothing if there are none)."""
    studies = _studies(pages_dir)
    here = str(_front_matter(pages_dir / current)["number"])
    cards = []
    for frm, to, kind, why in related_links(pages_dir):
        if here not in (frm, to):
            continue
        to_earlier, from_later = RELATION_LABELS[kind]
        other, label = (to, to_earlier) if frm == here else (frm, from_later)
        stem, meta = studies[other]
        cards.append(
            (
                int(other),
                f'<a class="link-card" href="{stem}.html">'
                f'<div class="kicker">{escape(label)}</div>'
                f'<div class="title">{int(other):02d} · {escape(meta["title"])}</div>'
                f'<p class="desc">{escape(why)}</p>'
                f'<div class="date">Data: {escape(str(meta.get("data-period", "")))}</div></a>',
            )
        )
    if not cards:
        return HTML("")
    body = "".join(card for _, card in sorted(cards))
    return HTML(
        '<section class="related" aria-labelledby="related-heading">'
        '<h2 id="related-heading" class="related-heading">Related case studies</h2>'
        f'<div class="link-cards">{body}</div></section>'
    )


def prev_next(current: str, pages_dir: Path) -> HTML:
    """Back-to-list and next-study cards at the end of a case study (Peak-End)."""
    pages = sorted(
        (int(meta["number"]), p.stem, meta)
        for p in pages_dir.glob("*.qmd")
        if not p.name.startswith("_") and "number" in (meta := _front_matter(p))
    )
    stems = [stem for _, stem, _ in pages]
    i = stems.index(Path(current).stem)
    later = pages[i + 1 :]
    nxt = ""
    if later:
        num, stem, meta = later[0]
        nxt = (
            f'<a class="link-card next" href="{stem}.html"><div class="kicker">Next →</div>'
            f'<div class="title">{num:02d} · {escape(meta["title"])}</div></a>'
        )
    return HTML(
        '<nav class="prevnext" aria-label="More case studies">'
        '<a class="link-card" href="index.html"><div class="kicker">← All case studies</div>'
        f'<div class="title">Back to the list</div></a>{nxt}</nav>'
    )
