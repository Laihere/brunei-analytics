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
    """`link` is the glossary filtered to this study, e.g. "../glossary.html?study=07"."""
    compare = "".join(
        f"<li><b>{escape(glossary[k]['term'])}:</b> {escape(glossary[k]['definition'])}</li>"
        for k in e.get("compare", [])
    )
    compare = f'<p class="term-vs">Not the same as</p><ul>{compare}</ul>' if compare else ""
    return (
        f'<div class="term-pop" id="term-{e["key"]}" popover>'
        f'<p class="term-name">{escape(e["term"])}</p><p>{escape(e["definition"])}</p>{compare}'
        f'{basis_line(e)}<a href="{link}#{e["key"]}">All terms used in this study →</a></div>'
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
    number = Path(current).stem.split("-", 1)[0]
    link = f"{glossary_link}?study={number}"
    pops = "".join(_popover(glossary[k], glossary, link) for k in used)
    return HTML(f'<div class="term-pops">{pops}</div>{_SCRIPT}')


STUDY_PAGES = ROOT / "dashboard" / "case-studies"


def study_name(stem: str) -> tuple[str, str]:
    """ "07-trade" → ("07", "Trade"); "01-cost-of-living" → ("01", "Cost of living")."""
    number, slug = stem.split("-", 1)
    return number, slug.replace("-", " ").capitalize()


def terms_by_study(pages_dir: Path = STUDY_PAGES) -> dict[str, list[str]]:
    """Term key → page stems of the case studies that mark it, in study order."""
    out: dict[str, list[str]] = {}
    for page in sorted(pages_dir.glob("[0-9]*.qmd")):
        for key in terms_used(page.read_text()):
            out.setdefault(key, []).append(page.stem)
    return out


_FILTER_SCRIPT = """<script>
// Glossary search and case-study chips (shared/glossary.py). Filters the entries by their
// data-text and data-studies attributes; the address keeps the filter (?find=…&study=07), so a
// filtered list can be shared or linked from a case study. Without JavaScript every term shows.
(() => {
  const box = document.querySelector(".glossary-filters");
  const list = document.querySelector("dl.glossary");
  if (!box || !list) return;
  const entries = [...list.querySelectorAll(".term-entry")];
  const search = box.querySelector("#term-search");
  const chips = [...box.querySelectorAll(".chip")];
  const count = document.querySelector(".glossary-count");
  const params = new URLSearchParams(location.search);
  let study = params.get("study") || "";
  if (!chips.some((c) => c.dataset.study === study)) study = "";
  search.value = params.get("find") || "";  // not "q": Quarto's site search uses it

  function update(save) {
    const words = search.value.toLowerCase().split(/\\s+/).filter(Boolean);
    let shown = 0;
    for (const e of entries) {
      const inStudy = !study || e.dataset.studies.split(" ").includes(study);
      const match = inStudy && words.every((w) => e.dataset.text.includes(w));
      e.hidden = !match;
      if (match) shown += 1;
    }
    chips.forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.study === study)));
    const chip = chips.find((c) => c.dataset.study === study);
    const where = study ? ` used in ${chip.textContent}` : "";
    count.textContent = shown
      ? `Showing ${shown} of ${entries.length} terms${where}`
      : "No terms match. Try another word, or choose All terms.";
    if (save) {
      const p = new URLSearchParams();
      if (search.value.trim()) p.set("find", search.value.trim());
      if (study) p.set("study", study);
      const qs = p.toString();
      history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash);
    }
  }

  chips.forEach((c) =>
    c.addEventListener("click", () => {
      study = c.dataset.study;
      update(true);
    })
  );
  search.addEventListener("input", () => update(true));
  box.hidden = false;
  update(false);
  // A link to one term (#key, e.g. "Not the same as") always shows it, even if the filter
  // would hide it: the filter is cleared first.
  function reveal() {
    const target = location.hash && document.getElementById(location.hash.slice(1));
    if (target && target.closest(".term-entry")?.hidden) {
      study = "";
      search.value = "";
      update(true);
    }
    if (target) target.scrollIntoView();
  }
  addEventListener("hashchange", reveal);
  reveal();
})();
</script>"""


def glossary_page(pages_dir: Path = STUDY_PAGES, study_link: str = "case-studies/") -> HTML:
    """Every term, A–Z, with search, case-study chips and a "Used in" line for each term."""
    glossary = load_glossary()
    used_in = terms_by_study(pages_dir)
    studies = sorted({stem for stems in used_in.values() for stem in stems})
    chips = (
        '<button type="button" class="chip" data-study="" aria-pressed="true">All terms</button>'
    )
    for stem in studies:
        number, name = study_name(stem)
        chips += (
            f'<button type="button" class="chip" data-study="{number}" aria-pressed="false">'
            f"{number} {escape(name)}</button>"
        )
    filters = (
        "<!-- Hidden until the script runs, so visitors without JavaScript see the plain list. -->"
        '<div class="glossary-filters study-filters" role="search" hidden>'
        '<label for="term-search" class="visually-hidden">Search the glossary</label>'
        '<input id="term-search" type="search" placeholder="Search terms and definitions" '
        'autocomplete="off">'
        '<div class="chips" role="group" aria-label="Show terms used in a case study">'
        f"{chips}</div>"
        '</div><p class="filter-count glossary-count" aria-live="polite"></p>'
    )
    items = []
    for e in sorted(glossary.values(), key=lambda e: e["term"].lower()):
        compare = ", ".join(
            f'<a href="#{k}">{escape(glossary[k]["term"])}</a>' for k in e.get("compare", [])
        )
        compare = f'<p class="term-vs-line">Not the same as: {compare}</p>' if compare else ""
        stems = used_in.get(e["key"], [])
        links = ", ".join(
            f'<a href="{study_link}{stem}.html">{" ".join(study_name(stem))}</a>' for stem in stems
        )
        used = f'<p class="term-used">Used in: {links}</p>' if stems else ""
        text = f"{e['term']} {e['definition']}".lower()
        numbers = " ".join(study_name(stem)[0] for stem in stems)
        items.append(
            f'<div class="term-entry" data-studies="{numbers}" data-text="{escape(text)}">'
            f'<dt id="{e["key"]}">{escape(e["term"])}</dt>'
            f"<dd><p>{escape(e['definition'])}</p>{compare}{basis_line(e)}{used}</dd></div>"
        )
    return HTML(f'{filters}<dl class="glossary">{"".join(items)}</dl>{_FILTER_SCRIPT}')


def glossary_references() -> HTML:
    """APA reference list of every source cited by a glossary term, A–Z, collapsed like a case
    study's references."""
    used = {s.key: s for e in load_glossary().values() for s in e["source_refs"]}
    refs = sorted(used.values(), key=lambda s: s.reference.lower())
    items = "".join(f"<li>{s.reference_html}</li>" for s in refs)
    return HTML(
        '<section class="detail-group" aria-label="Sources of the definitions">'
        "<details><summary>Sources of the definitions (APA)</summary><div>"
        f'<ul class="references glossary-references">{items}</ul></div></details></section>'
    )
