"""Context sources: news, journal articles and official publications cited for background
(DATA_USE_POLICY.md §7). They are never used for charted numbers.

Each case study lists its context sources in `context.yml`; every entry is checked by a
person before it is added (rule 5) and logged in CONTEXT_SOURCES.md.
"""

from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

import yaml

KINDS = {"news", "journal", "official", "book"}  # book: textbooks and handbooks


@dataclass(frozen=True)
class ContextSource:
    key: str  # short id used on the page, e.g. "haque2011"
    kind: str  # news | journal | official | book
    authors: tuple[str, ...]  # APA form, e.g. ("Haque, M. O.",); an organisation is one entry
    published: str  # ISO date, or a year; "" for undated documents (APA "n.d.")
    title: str  # as APA prints it: sentence case, proper nouns kept (typed by hand)
    container: str  # newspaper, journal or publisher
    url: str
    accessed: str  # ISO date the source was opened and checked
    volume: str = ""
    issue: str = ""
    pages: str = ""
    doi: str = ""
    archive_url: str = ""  # web.archive.org copy, required for news (rule 7)
    note: str = ""  # e.g. where a reprint was read

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"{self.key}: kind must be one of {sorted(KINDS)}")
        if not self.authors:
            raise ValueError(f"{self.key}: needs an author (person or organisation)")
        date.fromisoformat(self.accessed)
        if self.kind == "news" and not self.archive_url:
            raise ValueError(f"{self.key}: news sources need an archived copy (policy §7 rule 7)")

    @property
    def year(self) -> str:
        return self.published[:4] or "n.d."

    def cite(self) -> str:
        """APA in-text citation, e.g. "Haque & Haque, 2018"."""
        surnames = [a.split(",")[0] for a in self.authors]
        if len(surnames) == 1:
            who = surnames[0]
        elif len(surnames) == 2:
            who = f"{surnames[0]} & {surnames[1]}"
        else:
            who = f"{surnames[0]} et al."
        return f"{who}, {self.year}"


def _authors(names: tuple[str, ...]) -> str:
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + ", & " + names[-1]


def _date(p: str) -> str:
    if not p:
        return "n.d."
    if len(p) == 4:
        return p
    d = date.fromisoformat(p)
    return f"{d.year}, {d:%B} {d.day}"


def apa_context_reference(s: ContextSource, html: bool = False) -> str:
    """APA 7 reference for a news article, journal article or official publication."""
    esc = escape if html else (lambda t: t)
    em = (lambda t: f"<em>{escape(t)}</em>") if html else (lambda t: t)
    who = esc(_authors(s.authors).rstrip("."))
    title = esc(s.title)
    if s.kind == "journal":
        vol = em(s.volume) + (f"({esc(s.issue)})" if s.issue else "")
        body = f"{title}. {em(s.container)}, {vol}" + (f", {esc(s.pages)}" if s.pages else "") + "."
    elif s.kind == "news":
        body = f"{title}. {em(s.container)}."
    else:  # official or book: the publisher is only repeated when it isn't the author
        body = em(s.title) + "." + (f" {esc(s.container)}." if s.container not in s.authors else "")
    link = f"https://doi.org/{s.doi}" if s.doi else s.url
    link = f'<a href="{escape(link)}">{escape(link)}</a>' if html else link
    extra = f" {esc(s.note)}" if s.note else ""
    archived = ""
    if s.archive_url:
        a = f'<a href="{escape(s.archive_url)}">archived copy</a>' if html else s.archive_url
        archived = f" ({a})"
    return f"{who}. ({_date(s.published)}). {body}{extra} {link}{archived}"


def load_context(path: Path) -> dict[str, ContextSource]:
    """Read a case study's context.yml into {key: ContextSource}."""
    entries = yaml.safe_load(path.read_text()) or []
    out = {}
    for e in entries:
        e["authors"] = tuple(e["authors"])
        e = {k: v if k == "authors" else str(v) for k, v in e.items()}
        s = ContextSource(**e)
        if s.key in out:
            raise ValueError(f"Duplicate context key: {s.key}")
        out[s.key] = s
    return out
