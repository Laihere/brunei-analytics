import pandas as pd
import pytest

from shared.fetch import cached_frame
from shared.outputs import credit_for, read_output, write_output
from shared.provenance import (
    OWNER_MISSING,
    Provenance,
    apa_year_labels,
    attribution,
    short_credit,
)
from shared.sources import get_source

CPI = Provenance(
    source="datagovbn",
    title="Consumer Price Index 2025",
    page_url="https://www.data.gov.bn/consumer-price-index-2025/",
    accessed="2026-10-14",
    owner="Department of Statistics, JPES",
    published="2026-07-13",
)
GDP = Provenance(
    source="datagovbn",
    title="Gross Domestic Product Per Capita at Current Prices",
    page_url="https://www.data.gov.bn/example/",
    accessed="2026-10-02",
    owner=OWNER_MISSING,
)
WDI = Provenance(
    source="worldbank",
    title="Inflation, consumer prices (annual %)",
    page_url="https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=BN",
    accessed="2026-10-09",
)


def test_unapproved_source_is_refused():
    with pytest.raises(ValueError, match="not an approved source"):
        get_source("imf")
    with pytest.raises(ValueError):
        Provenance(source="owid", title="x", page_url="x", accessed="2026-10-14")


def test_bad_access_date_is_refused():
    with pytest.raises(ValueError):
        Provenance(source="datagovbn", title="x", page_url="x", accessed="14/10/2026")


def test_datagovbn_reference_is_apa_with_retrieval_date():
    assert attribution(CPI) == (
        "Department of Statistics, JPES. (2026). Consumer price index 2025 [Data set]. "
        "Brunei Open Data. Retrieved October 14, 2026, from "
        "https://www.data.gov.bn/consumer-price-index-2025/"
    )


def test_apa_html_italicises_title_and_links_url():
    html = attribution(CPI, html=True)
    assert "<em>Consumer price index 2025</em> [Data set]" in html
    assert '<a href="https://www.data.gov.bn/consumer-price-index-2025/">' in html


def test_missing_owner_moves_title_to_author_position():
    text = attribution(GDP)
    assert text.startswith(
        "Gross domestic product per capita at current prices [Data set]. (n.d.)."
    )
    assert OWNER_MISSING not in text
    assert "Retrieved October 2, 2026" in text


def test_cc_by_reference_names_publisher_and_licence():
    text = attribution(WDI)
    assert text.startswith("World Bank. (n.d.). Inflation, consumer prices (annual %) [Data set].")
    assert "World Development Indicators. Licensed under CC BY 4.0." in text


def test_same_author_and_year_get_apa_suffixes_in_title_order():
    pct = Provenance(
        source="datagovbn",
        title="Percentage Change in Customer Price Index 2025",
        page_url="https://www.data.gov.bn/pct/",
        accessed="2026-10-14",
        owner="Department of Statistics, JPES",
        published="2026-07-11",
    )
    labels = apa_year_labels([pct, CPI, GDP])
    assert labels == {CPI: "2026a", pct: "2026b", GDP: "n.d."}
    assert attribution(pct, year=labels[pct]).startswith("Department of Statistics, JPES. (2026b).")


def test_identical_titles_are_ordered_by_edition_and_undated_get_hyphen():
    def crime(edition):
        return Provenance(
            source="datagovbn",
            title="Crime Statistics",
            page_url=f"https://www.data.gov.bn/crime-{edition}/",
            accessed="2026-10-16",
            owner="Royal Brunei Police Force",
            edition=edition,
            published="2025-12-17",
        )

    c13, c12 = crime("2013"), crime("2012")
    assert apa_year_labels([c13, c12, c13]) == {c12: "2025a", c13: "2025b"}
    wdi2 = Provenance(
        source="worldbank", title="Consumer price index", page_url="x", accessed="2026-10-09"
    )
    assert apa_year_labels([WDI, wdi2]) == {wdi2: "n.d.-a", WDI: "n.d.-b"}


def test_short_credit_has_year_retrieval_date_and_disclaimer():
    text = short_credit([CPI, GDP, WDI])
    assert "Department of Statistics, JPES (2026), via data.gov.bn, retrieved 14 Oct 2026" in text
    assert "data.gov.bn (owner not stated) (n.d.), retrieved 2 Oct 2026" in text
    assert "World Bank (n.d.), World Development Indicators, retrieved 9 Oct 2026" in text
    assert "Analysis by Muhd Lai Razi Muhd Silmi with AI assistance (Claude)" in text
    assert text.endswith("not an official government publication.")


def test_short_credit_requires_a_source():
    with pytest.raises(ValueError):
        short_credit([])


def test_output_roundtrip_keeps_provenance(tmp_path):
    df = pd.DataFrame({"year": [2024, 2025], "cpi": [100.0, 99.6]})
    path = write_output(df, tmp_path / "cpi.csv", [CPI], notes="Annual mean of monthly index.")
    back, prov, notes = read_output(path)
    assert back.equals(df)
    assert prov == [CPI]
    assert notes == "Annual mean of monthly index."
    assert "Department of Statistics, JPES" in credit_for(path)


def test_output_requires_notes_and_sources(tmp_path):
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError):
        write_output(df, tmp_path / "a.csv", [], notes="x")
    with pytest.raises(ValueError):
        write_output(df, tmp_path / "a.csv", [CPI], notes=" ")


def test_cached_frame_calls_loader_once(tmp_path):
    calls = []

    def loader():
        calls.append(1)
        return pd.DataFrame({"year": [2025], "value": [1.5]})

    for _ in range(2):
        df, prov = cached_frame(
            "worldbank", "test", "Test indicator", "https://example.org", loader, raw_dir=tmp_path
        )
    assert len(calls) == 1
    assert df["value"].tolist() == [1.5]
    assert prov.source == "worldbank"


def test_original_source_is_named_in_every_credit():
    wb = Provenance(
        source="worldbank",
        title="Inflation, consumer prices (annual %)",
        page_url="https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=BN",
        accessed="2026-10-15",
        original_source="IMF International Financial Statistics",
    )
    assert "Original data from IMF International Financial Statistics." in attribution(wb)
    assert "original data from IMF International Financial Statistics" in short_credit([wb])


def test_non_english_title_gets_bracketed_translation():
    p = Provenance(
        source="datagovbn",
        title="Statistik Industri Agrimakanan",
        page_url="https://www.data.gov.bn/statistik-industri-agrimakanan/",
        accessed="2026-10-16",
        owner="Ministry of Industry and Primary Resources",
        published="2025-12-22",
        title_translation="Agrifood industry statistics",
    )
    assert attribution(p).startswith(
        "Ministry of Industry and Primary Resources. (2025). Statistik industri agrimakanan "
        "[Agrifood industry statistics] [Data set]."
    )
    assert "<em>Statistik industri agrimakanan</em> [Agrifood industry statistics]" in attribution(
        p, html=True
    )


def test_squarify_fills_the_box_with_areas_in_proportion():
    from shared.svg import squarify

    values = [50, 30, 12, 5, 2, 1]
    rects = squarify(values, 0, 0, 300, 200)
    areas = [w * h for _, _, w, h in rects]
    assert sum(areas) == pytest.approx(300 * 200)
    for v, a in zip(values, areas, strict=True):
        assert a == pytest.approx(v / sum(values) * 300 * 200)
    for x, y, w, h in rects:  # every block inside the box
        assert x >= -1e-9 and y >= -1e-9 and x + w <= 300 + 1e-9 and y + h <= 200 + 1e-9


def test_svg_labels_use_readable_ink_never_the_series_colour():
    from shared.charts import CATEGORICAL, CONTEXT, TEAL_500
    from shared.svg import contrast, text_colour

    for fill in [TEAL_500, CATEGORICAL[1], CONTEXT]:
        assert contrast(text_colour(fill), fill) >= 4.5


def test_treemap_labels_only_blocks_they_fit_and_every_block_has_a_tooltip():
    from shared.svg import Block, treemap_panel

    out = treemap_panel(
        [Block("Large block", 90, "#c3c2b7", "90%"), Block("Tiny block", 1, "#c3c2b7", "1%")],
        0,
        0,
        300,
        200,
    )
    assert out.count("<title>") == 2
    assert ">Large block</text>" in out and ">Tiny block</text>" not in out


def test_district_shapes_cover_the_four_districts_and_credit_geoboundaries():
    from shared.paths import CASE_STUDIES

    shapes, prov, notes = read_output(CASE_STUDIES / "_shared" / "outputs" / "brunei_districts.csv")
    assert set(shapes.district) == {"Belait", "Brunei-Muara", "Temburong", "Tutong"}
    assert [p.source for p in prov] == ["geoboundaries"]
    assert "not an official map" in notes
    assert "geoBoundaries" in short_credit(prov)


def test_district_map_needs_every_district_and_labels_each():
    from shared.paths import CASE_STUDIES
    from shared.svg import STEPS, Area, district_map

    shapes = pd.read_csv(CASE_STUDIES / "_shared" / "outputs" / "brunei_districts.csv")
    areas = [Area(d, STEPS[0], "1%", f"{d}: 1%") for d in shapes.district]
    out = district_map(shapes, areas, 0, 0, 300)
    assert out.count("<title>") == 4 and out.count("1%</tspan>") == 4
    with pytest.raises(AssertionError):
        district_map(shapes, areas[:3], 0, 0, 300)


def test_pages_with_maps_link_geoboundaries_and_say_not_official():
    from shared.paths import ROOT

    for page in (ROOT / "dashboard" / "case-studies").glob("[0-9]*.qmd"):
        text = page.read_text()
        if "districts_maps(" in text or "district_map(" in text:
            assert "https://www.geoboundaries.org/" in text, page.name
            assert "not an official map" in text, page.name
