import re
from html import unescape

import pandas as pd
import plotly.express as px
import plotly.offline
import pytest

from shared.charts import CONTEXT, TEAL_500, highlight
from shared.components import chart_card, method_and_sources, prev_next, stat_tile, stat_tiles
from shared.paths import ROOT
from shared.provenance import Provenance

PROV = [
    Provenance(
        source="datagovbn",
        title="Consumer Price Index 2025",
        page_url="https://www.data.gov.bn/consumer-price-index-2025/",
        accessed="2026-10-14",
        owner="Department of Statistics, JPES",
    )
]
DF = pd.DataFrame(
    {"year": [2024, 2025, 2024, 2025], "series": ["A", "A", "B", "B"], "value": [1, 2, 1, 1]}
)


def test_plotly_bundle_matches_installed_version():
    meta = (ROOT / "dashboard" / "case-studies" / "_metadata.yml").read_text()
    pinned = re.search(r"plotly-basic-([\d.]+)\.min\.js", meta).group(1)
    assert pinned == plotly.offline.get_plotlyjs_version()


def test_highlight_colours_one_series_and_draws_it_last():
    fig = highlight(px.line(DF, x="year", y="value", color="series"), "A")
    lines = [t for t in fig.data if t.mode == "lines"]
    assert [t.line.color for t in lines] == [CONTEXT, TEAL_500]
    assert fig.data[-1].text == ("A",)  # end label sits on top


def test_highlight_bars_by_category():
    bars = pd.DataFrame({"g": ["x", "y"], "v": [2, 1]})
    fig = highlight(px.bar(bars, x="v", y="g", orientation="h"), "x")
    assert tuple(fig.data[0].marker.color) == (TEAL_500, CONTEXT)


def test_stat_tile_never_relies_on_colour_alone():
    html = stat_tile("Food CPI", "+4.1%", "1.3 pts", "vs 2024", "up-bad")
    assert "▲" in html and "(worsening)" in html and 'class="up-bad"' in html


def test_stat_tile_escapes_text():
    assert "<script>" not in stat_tile("<script>", "1")


def test_stat_tiles_limit():
    with pytest.raises(ValueError):
        stat_tiles(*[stat_tile("a", "1")] * 4)


def test_chart_card_has_credit_table_and_alt_text():
    fig = px.line(DF, x="year", y="value", color="series")
    html = chart_card(fig, "Takeaway", "Index · 2024–2025", "A rose, B flat", PROV, DF).data
    assert "Department of Statistics, JPES (n.d.), via data.gov.bn, retrieved 14 Oct 2026" in html
    assert 'class="table-box" tabindex="0"' in html  # table scrolls in its own box
    assert "Show data table" in html and "<table" in html
    assert 'aria-label="A rose, B flat"' in html
    assert "plotly.js v" not in html  # library loaded once per page, not embedded
    assert '"fixedrange":true' in html and '"dragmode":false' in html  # no accidental zoom


def test_chart_card_requires_alt_text():
    with pytest.raises(ValueError):
        chart_card(px.line(DF, x="year", y="value"), "t", "s", " ", PROV, DF)


def test_method_and_sources_lists_full_attribution():
    html = unescape(method_and_sources(PROV, "Annual mean.", ["Download", "Clean"]).data)
    assert "<em>Consumer price index 2025</em> [Data set]. Brunei Open Data." in html
    assert "Not an official publication" in html
    assert "with AI assistance (Claude)" in html and "how-ai-was-used" in html


def test_prev_next_links_to_following_study(tmp_path):
    for n, stem in [("01", "01-a"), ("02", "02-b")]:
        (tmp_path / f"{stem}.qmd").write_text(f'---\ntitle: "Study {n}"\nnumber: "{n}"\n---\n')
    (tmp_path / "_template.qmd").write_text('---\nnumber: "NN"\n---\n')
    html = prev_next("01-a.qmd", tmp_path).data
    assert 'href="02-b.html"' in html and "02 · Study 02" in html
    assert 'href="02' not in prev_next("02-b.qmd", tmp_path).data


def test_public_policy_hides_internal_sections():
    from shared.policy import public_policy

    text = public_policy((ROOT / "DATA_USE_POLICY.md").read_text(), "https://example.org/repo")
    assert "Open questions for EGNC" not in text
    assert "Our working rules" not in text
    assert "How the code applies this policy" not in text
    assert "(§4)" not in text
    headings = re.findall(r"(?m)^## (\d+)\.", text)
    assert headings == ["1", "2", "3", "4"]
    assert "Approved sources" in text
    assert "[full policy](https://example.org/repo/blob/main/DATA_USE_POLICY.md)" in text
    assert "[DATA_SOURCES.md](https://example.org/repo/blob/main/DATA_SOURCES.md)" in text
    assert "`brunei_analytics`" not in text


def test_home_shows_five_latest_and_links_to_all():
    home = (ROOT / "dashboard" / "index.qmd").read_text()
    assert re.search(r"max-items:\s*5\b", home)
    assert 'sort: "number desc"' in home
    assert 'href="case-studies/index.html"' in home
    assert "upcoming.yml" not in home  # "Coming soon" cards live on the case studies page only


def test_case_study_filters_match_card_attributes():
    pages = ROOT / "dashboard" / "case-studies"
    script = (pages / "_study-filters.html").read_text()
    index = (pages / "index.qmd").read_text()
    cards = (ROOT / "dashboard" / "_templates" / "study-cards.ejs").read_text()
    assert "include-after-body: _study-filters.html" in index
    for control in ("study-search", "study-sort"):
        assert f'id="{control}"' in index and f"#{control}" in script
    # Every data-* attribute the script reads must be written by the card template.
    for attr in re.findall(r"dataset\.(\w+)", script):
        kebab = re.sub(r"([A-Z])", lambda m: "-" + m.group(1).lower(), attr)
        assert f"data-{kebab}" in cards or attr == "listingDateSort", attr
