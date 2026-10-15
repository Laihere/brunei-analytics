"""Every published case study follows the standard structure (DESIGN.md §4.1)."""

import re

import pytest

from shared.components import _front_matter
from shared.paths import ROOT

PAGES = sorted((ROOT / "dashboard" / "case-studies").glob("[0-9]*.qmd"))
FRONT_MATTER = ["title", "description", "number", "topic", "data-period", "read-time", "date"]
REQUIRED = {
    "introduction": r"::: \{\.study-intro\}",
    "key numbers": r"stat_tiles\(",
    "main chart": r"chart_card\(",
    "conclusion": r"^## Conclusion$",
    "side note": r"callout-caution[^}]*title=\"What this doesn't tell us\"",
    "method and references": r"method_and_sources\(",
    "next study": r"prev_next\(",
}


def test_there_is_at_least_one_case_study():
    assert PAGES


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.stem)
def test_front_matter(page):
    meta = _front_matter(page)
    missing = [k for k in FRONT_MATTER if not meta.get(k)]
    assert not missing, f"{page.name} front matter missing {missing}"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.stem)
def test_standard_sections_in_order(page):
    text = page.read_text()
    positions = {}
    for name, pattern in REQUIRED.items():
        m = re.search(pattern, text, re.MULTILINE)
        assert m, f"{page.name} is missing its {name}"
        positions[name] = m.start()
    assert list(positions) == sorted(positions, key=positions.get), (
        f"{page.name}: sections out of order"
    )
    body = re.findall(r"^## (?!Conclusion)", text, re.MULTILINE)
    assert 2 <= len(body) <= 4, f"{page.name}: use 2–4 body sections (found {len(body)})"
