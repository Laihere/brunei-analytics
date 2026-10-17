"""Glossary terms: pop-up definitions on case study pages and the Glossary page (DESIGN.md §5).

On a page, mark a term once with a Pandoc span:
    [share of businesses]{.term term="share-of-businesses"}
`glossary_popovers` (called at the end of each case study) adds the definitions for the terms
that page uses, and a small script turns each marked term into a button that opens a pop-up.
Browsers without the popover feature get a plain tooltip instead.

Every term says where its definition comes from (`basis` in glossary.yml):
    standard   an official or statistical definition, cited ("Based on: …")
    publisher  the term as the data's publisher uses it, cited ("As used by the publisher: …")
    site       a measure defined for these case studies ("Defined for this site")
Sources are in glossary_sources.yml: documents, or datasets already credited in a case study.
"""

import json
import re
from dataclasses import dataclass
from html import escape
from pathlib import Path

import yaml

from shared.context import ContextSource, apa_context_reference
from shared.html import RawHTML as HTML
from shared.paths import CASE_STUDIES, ROOT
from shared.provenance import Provenance, apa_reference, apa_year_labels

GLOSSARY = ROOT / "dashboard" / "glossary.yml"
GLOSSARY_SOURCES = ROOT / "dashboard" / "glossary_sources.yml"
TERM = re.compile(r'\{\.term term="([a-z0-9-]+)"\}')
BASIS = {
    "standard": "Based on",
    "publisher": "As used by the publisher",
    "site": "Defined for this site",
}


@dataclass(frozen=True)
class GlossarySource:
    key: str
    label: str  # in-text form, e.g. "Department of Statistics (n.d.)"
    url: str
    reference: str  # APA 7, plain text
    reference_html: str


def _dataset_provenance() -> dict[str, Provenance]:
    """Every dataset credited in a case study's outputs, by dataset page."""
    found = {}
    for meta in sorted(CASE_STUDIES.glob("[0-9]*/outputs/*.meta.json")):
        for d in json.loads(meta.read_text())["sources"]:
            p = Provenance.from_dict(d)
            found.setdefault(p.page_url, p)
    return found


def load_sources(path: Path = GLOSSARY_SOURCES) -> dict[str, GlossarySource]:
    entries = yaml.safe_load(path.read_text()) or []
    datasets = _dataset_provenance()
    docs, sets = {}, {}
    for e in entries:
        key = e["key"]
        if key in docs or key in sets:
            raise ValueError(f"Duplicate glossary source: {key}")
        if e["kind"] == "dataset":
            if e["page_url"] not in datasets:
                raise ValueError(f"{key}: no case study output credits {e['page_url']}")
            sets[key] = datasets[e["page_url"]]
        else:
            e = {k: tuple(v) if k == "authors" else str(v) for k, v in e.items()}
            docs[key] = ContextSource(**e)
    out = {}
    for key, c in docs.items():
        who = c.cite().rsplit(", ", 1)[0]
        url = f"https://doi.org/{c.doi}" if c.doi else c.url
        out[key] = GlossarySource(
            key, f"{who} ({c.year})", url, apa_context_reference(c), apa_context_reference(c, True)
        )
    years = apa_year_labels(list(sets.values()))  # 2025a, 2025b… for one owner and year
    for key, p in sets.items():
        y = years[p]
        out[key] = GlossarySource(
            key, f"{p.owner} ({y})", p.page_url, apa_reference(p, year=y),
            apa_reference(p, html=True, year=y),
        )  # fmt: skip
    return out


def load_glossary(path: Path = GLOSSARY, sources_path: Path = GLOSSARY_SOURCES) -> dict[str, dict]:
    entries = yaml.safe_load(path.read_text())
    out = {e["key"]: {**e, "definition": " ".join(e["definition"].split())} for e in entries}
    sources = load_sources(sources_path)
    for e in out.values():
        missing = [k for k in e.get("compare", []) if k not in out]
        if missing:
            raise ValueError(f"{e['key']}: compares with unknown terms {missing}")
        if e.get("basis") not in BASIS:
            raise ValueError(f"{e['key']}: basis must be one of {list(BASIS)}")
        unknown = [k for k in e.get("sources", []) if k not in sources]
        if unknown:
            raise ValueError(f"{e['key']}: unknown sources {unknown} (glossary_sources.yml)")
        if e["basis"] != "site" and not e.get("sources"):
            raise ValueError(f"{e['key']}: a {e['basis']} definition needs a source")
        e["source_refs"] = [sources[k] for k in e.get("sources", [])]
    return out


def basis_line(e: dict) -> str:
    """ "Based on: <a>UN Statistics Division (2006)</a>", or "Defined for this site." """
    if e["basis"] == "site":
        return f'<p class="term-basis">{BASIS["site"]}: see each case study\'s method.</p>'
    links = "; ".join(
        f'<a href="{escape(s.url)}" rel="noopener">{escape(s.label)}</a>' for s in e["source_refs"]
    )
    return f'<p class="term-basis">{BASIS[e["basis"]]}: {links}</p>'


def terms_used(text: str) -> list[str]:
    return list(dict.fromkeys(TERM.findall(text)))


def _popover(e: dict, glossary: dict, link: str) -> str:
    compare = "".join(
        f"<li><b>{escape(glossary[k]['term'])}:</b> {escape(glossary[k]['definition'])}</li>"
        for k in e.get("compare", [])
    )
    compare = f'<p class="term-vs">Not the same as</p><ul>{compare}</ul>' if compare else ""
    return (
        f'<div class="term-pop" id="term-{e["key"]}" popover>'
        f'<p class="term-name">{escape(e["term"])}</p><p>{escape(e["definition"])}</p>{compare}'
        f'{basis_line(e)}<a href="{link}#{e["key"]}">All terms in the glossary →</a></div>'
    )


_SCRIPT = """<script>
// Glossary terms (shared/glossary.py): a marked term becomes a button that opens its pop-up,
// placed next to the term. Without popover support, the definition becomes a tooltip.
(() => {
  const supported = HTMLElement.prototype.hasOwnProperty("popover");
  let last = null;
  document.querySelectorAll("span.term[data-term]").forEach((span) => {
    const pop = document.getElementById("term-" + span.dataset.term);
    if (!pop) return;
    if (!supported) {
      span.title = pop.querySelector("p:nth-of-type(2)").textContent;
      span.tabIndex = 0;
      return;
    }
    const b = document.createElement("button");
    b.type = "button";
    b.className = "term";
    b.setAttribute("popovertarget", pop.id);
    b.append(...span.childNodes);
    b.addEventListener("click", () => (last = b));
    span.replaceWith(b);
  });
  document.querySelectorAll(".term-pop").forEach((pop) => {
    pop.addEventListener("toggle", (e) => {
      if (e.newState !== "open" || !last) return;
      const r = last.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight;
      const below = r.bottom + 8 + h < innerHeight;
      pop.style.top = (below ? r.bottom + 8 : Math.max(8, r.top - h - 8)) + "px";
      pop.style.left = Math.min(Math.max(8, r.left), innerWidth - w - 8) + "px";
    });
  });
})();
</script>"""


def glossary_popovers(
    current: str, pages_dir: Path, glossary_link: str = "../glossary.html"
) -> HTML:
    """Definitions and script for the terms marked on this page (nothing if it marks none)."""
    used = terms_used((pages_dir / current).read_text())
    if not used:
        return HTML("")
    glossary = load_glossary()
    unknown = [k for k in used if k not in glossary]
    if unknown:
        raise ValueError(f"{current} uses terms missing from glossary.yml: {unknown}")
    pops = "".join(_popover(glossary[k], glossary, glossary_link) for k in used)
    return HTML(f'<div class="term-pops">{pops}</div>{_SCRIPT}')


def glossary_page() -> HTML:
    """Every term, A–Z, for the Glossary page."""
    glossary = load_glossary()
    items = []
    for e in sorted(glossary.values(), key=lambda e: e["term"].lower()):
        compare = ", ".join(
            f'<a href="#{k}">{escape(glossary[k]["term"])}</a>' for k in e.get("compare", [])
        )
        compare = f'<p class="term-vs-line">Not the same as: {compare}</p>' if compare else ""
        items.append(
            f'<dt id="{e["key"]}">{escape(e["term"])}</dt>'
            f"<dd><p>{escape(e['definition'])}</p>{compare}{basis_line(e)}</dd>"
        )
    return HTML(f'<dl class="glossary">{"".join(items)}</dl>')


def glossary_references() -> HTML:
    """APA reference list of every source cited by a glossary term, A–Z."""
    used = {s.key: s for e in load_glossary().values() for s in e["source_refs"]}
    refs = sorted(used.values(), key=lambda s: s.reference.lower())
    items = "".join(f"<li>{s.reference_html}</li>" for s in refs)
    return HTML(f'<ul class="references glossary-references">{items}</ul>')
