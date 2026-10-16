"""Glossary terms: pop-up definitions on case study pages and the Glossary page (DESIGN.md §5).

On a page, mark a term once with a Pandoc span:
    [share of businesses]{.term term="share-of-businesses"}
`glossary_popovers` (called at the end of each case study) adds the definitions for the terms
that page uses, and a small script turns each marked term into a button that opens a pop-up.
Browsers without the popover feature get a plain tooltip instead.
"""

import re
from html import escape
from pathlib import Path

import yaml
from IPython.display import HTML

from shared.paths import ROOT

GLOSSARY = ROOT / "dashboard" / "glossary.yml"
TERM = re.compile(r'\{\.term term="([a-z0-9-]+)"\}')


def load_glossary(path: Path = GLOSSARY) -> dict[str, dict]:
    entries = yaml.safe_load(path.read_text())
    out = {e["key"]: {**e, "definition": " ".join(e["definition"].split())} for e in entries}
    for e in out.values():
        missing = [k for k in e.get("compare", []) if k not in out]
        if missing:
            raise ValueError(f"{e['key']}: compares with unknown terms {missing}")
    return out


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
        f'<a href="{link}#{e["key"]}">All terms in the glossary →</a></div>'
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
            f"<dd><p>{escape(e['definition'])}</p>{compare}</dd>"
        )
    return HTML(f'<dl class="glossary">{"".join(items)}</dl>')
