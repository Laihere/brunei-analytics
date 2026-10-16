"""Context sources (DATA_USE_POLICY.md §7): APA references, rules, and every case study's file."""

import re

import pytest

from shared.components import method_and_sources
from shared.context import ContextSource, apa_context_reference, load_context
from shared.paths import CASE_STUDIES, ROOT

JOURNAL = ContextSource(
    key="haque2018",
    kind="journal",
    authors=("Haque, M. O.", "Haque, T. H."),
    published="2018",
    title="Evaluating the effects of the road safety system approach in Brunei",
    container="Transportation Research Part A: Policy and Practice",
    volume="118",
    pages="594–607",
    doi="10.1016/j.tra.2018.08.017",
    url="https://doi.org/10.1016/j.tra.2018.08.017",
    accessed="2026-10-16",
)
NEWS = dict(
    key="news",
    kind="news",
    authors=("Mohamad, L.",),
    published="2011-05-27",
    title="Royalty launches Blueprint Decade of Action for Road Safety",
    container="Borneo Bulletin",
    url="https://example.org/a",
    accessed="2026-10-16",
)


def test_journal_reference_and_citation_are_apa():
    assert apa_context_reference(JOURNAL) == (
        "Haque, M. O., & Haque, T. H. (2018). Evaluating the effects of the road safety system "
        "approach in Brunei. Transportation Research Part A: Policy and Practice, 118, 594–607. "
        "https://doi.org/10.1016/j.tra.2018.08.017"
    )
    assert JOURNAL.cite() == "Haque & Haque, 2018"


def test_news_reference_has_full_date_and_archive():
    s = ContextSource(**NEWS, archive_url="https://web.archive.org/x")
    text = apa_context_reference(s)
    assert text.startswith("Mohamad, L. (2011, May 27). Royalty launches Blueprint")
    assert "Borneo Bulletin." in text and text.endswith("(https://web.archive.org/x)")
    assert "<em>Borneo Bulletin</em>" in apa_context_reference(s, html=True)


def test_news_without_archive_is_refused():
    with pytest.raises(ValueError, match="archived copy"):
        ContextSource(**NEWS)


def test_context_joins_the_alphabetical_reference_list():
    from tests.test_shared import CPI

    html = str(method_and_sources([CPI], "notes", ["step"], context=[JOURNAL]).data)
    refs = re.findall(r"<li>(.*?)</li>", html.split("references")[1])
    assert [re.sub(r"<[^>]+>", "", r)[:5] for r in refs] == ["Depar", "Haque"]


@pytest.mark.parametrize(
    "path", sorted(CASE_STUDIES.glob("*/context.yml")), ids=lambda p: p.parent.name
)
def test_every_context_file_loads_and_is_logged(path):
    sources = load_context(path)
    log = (ROOT / "CONTEXT_SOURCES.md").read_text()
    for s in sources.values():
        assert s.title in log, f"{s.key} isn't in CONTEXT_SOURCES.md"
