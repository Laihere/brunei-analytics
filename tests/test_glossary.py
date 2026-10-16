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
