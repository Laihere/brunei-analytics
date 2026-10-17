"""Glossary pop-ups and item status (DESIGN.md §5 and §8)."""

import pandas as pd

from shared.charts import item_status, status_label, status_marker
from shared.glossary import glossary_page, glossary_popovers, load_glossary, terms_used


def test_glossary_entries_are_complete_and_comparisons_exist():
    g = load_glossary()
    for key, e in g.items():
        assert e["term"] and len(e["definition"]) > 20, key
    assert "share-of-market-value" in g["share-of-businesses"]["compare"]  # the pair links


def test_popovers_only_for_terms_on_the_page(tmp_path):
    page = tmp_path / "x.qmd"
    page.write_text('The [share of businesses]{.term term="share-of-businesses"} rose.')
    html = str(glossary_popovers("x.qmd", tmp_path).data)
    assert 'id="term-share-of-businesses" popover' in html
    assert "Not the same as" in html and "Share of market value" in html  # comparison shown
    assert 'id="term-median"' not in html
    assert terms_used(page.read_text()) == ["share-of-businesses"]
    (tmp_path / "plain.qmd").write_text("No terms.")
    assert str(glossary_popovers("plain.qmd", tmp_path).data) == ""


def test_glossary_page_lists_every_term_with_an_anchor():
    html = str(glossary_page().data)
    for key in load_glossary():
        assert f'<dt id="{key}">' in html


def test_item_status_continued_new_discontinued():
    df = pd.DataFrame(
        {"item": ["A", "A", "B", "B", "C", "C"], "year": [2012, 2013] * 3, "v": [1, 2, 0, 5, 4, 0]}
    )
    status = item_status(df, "item", "year", "v", 2012, 2013).to_dict()
    assert status == {"A": "continued", "B": "new", "C": "discontinued"}
    assert status_marker("new")["pattern"]["shape"] == "/"  # never colour alone
    assert "line" in status_marker("discontinued")
    assert status_label("B", "new", 2013) == "B (new in 2013)"
    assert status_label("A", "continued", 2013) == "A"


def test_every_term_says_where_its_definition_comes_from():
    """Standard and publisher terms cite a source; site terms say so (agreed 17 Oct 2026)."""
    from shared.glossary import BASIS, load_sources

    g = load_glossary()
    for key, e in g.items():
        assert e["basis"] in BASIS, key
        if e["basis"] != "site":
            assert e["source_refs"], key
    used = {s.key for e in g.values() for s in e["source_refs"]}
    assert used == set(load_sources()), "every glossary source is cited by some term"


def test_basis_line_in_popups_and_on_the_glossary_page(tmp_path):
    from shared.glossary import glossary_references

    page = tmp_path / "x.qmd"
    page.write_text(
        '[Re-exports]{.term term="re-exports"} and [share]{.term term="share-of-imports"}'
    )
    html = str(glossary_popovers("x.qmd", tmp_path).data)
    assert "Based on: <a" in html and "Department of Statistics (n.d.)" in html
    assert "Defined for this site" in html
    assert "As used by the publisher" in str(glossary_page().data)
    refs = str(glossary_references().data)
    assert "[Data set]" in refs and "archived copy" in refs and "n.d." in refs


def test_unknown_or_missing_sources_stop_the_build(tmp_path):
    import pytest

    bad = tmp_path / "g.yml"
    bad.write_text("- key: x\n  term: X\n  basis: standard\n  definition: A long enough text.\n")
    with pytest.raises(ValueError, match="needs a source"):
        load_glossary(bad)
    bad.write_text("- key: x\n  term: X\n  basis: guess\n  definition: A long enough text.\n")
    with pytest.raises(ValueError, match="basis"):
        load_glossary(bad)


def test_glossary_page_has_search_chips_and_used_in_lines(tmp_path):
    from shared.glossary import study_name

    (tmp_path / "01-cost-of-living.qmd").write_text('[CPI]{.term term="cpi"}')
    (tmp_path / "07-trade.qmd").write_text(
        '[CPI]{.term term="cpi"} [re-exports]{.term term="re-exports"}'
    )
    (tmp_path / "_template.qmd").write_text('[x]{.term term="median"}')  # not a study
    html = str(glossary_page(tmp_path).data)
    assert 'id="term-search"' in html and 'class="filter-count glossary-count"' in html
    assert 'data-study="07"' in html and ">07 Trade</button>" in html
    assert 'data-study="01"' in html and 'data-study=""' in html  # "All terms"
    entry = html[: html.index('<dt id="cpi">')].rsplit('<div class="term-entry"', 1)[1]
    assert entry.startswith(' data-studies="01 07"')
    assert 'Used in: <a href="case-studies/01-cost-of-living.html">01 Cost of living</a>' in html
    assert study_name("05-agrifood-processing") == ("05", "Agrifood processing")
    assert "history.replaceState" in html  # filter kept in the address


def test_popups_link_to_this_studys_terms(tmp_path):
    (tmp_path / "07-trade.qmd").write_text('[re-exports]{.term term="re-exports"}')
    html = str(glossary_popovers("07-trade.qmd", tmp_path).data)
    assert 'href="../glossary.html?study=07#re-exports"' in html


def test_glossary_references_are_collapsed():
    from shared.glossary import glossary_references

    html = str(glossary_references().data)
    assert html.startswith('<section class="detail-group"')
    assert "<details><summary>Sources of the definitions (APA)</summary>" in html
