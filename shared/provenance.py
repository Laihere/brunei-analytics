"""Where a piece of data came from, and the credit lines built from it."""

import json
from dataclasses import asdict, dataclass
from datetime import date
from html import escape
from pathlib import Path

from shared.sources import get_source

AUTHOR = "Muhd Lai Razi"
# AI-assistance disclosure (DATA_USE_POLICY.md §4, rule 10). The author is accountable for the
# work; the disclosure says plainly that an AI assistant helped build it.
BYLINE = f"{AUTHOR} with AI assistance (Claude)"
DISCLAIMER = "Not an official publication of the Government of Brunei Darussalam."
OWNER_MISSING = "Dataset owner not available."


@dataclass(frozen=True)
class Provenance:
    source: str  # key in shared.sources.SOURCES
    title: str
    page_url: str  # dataset or indicator page, linked in credits
    accessed: str  # ISO date the file was downloaded
    file_url: str = ""
    owner: str = ""  # data.gov.bn "Data Source Owner", copied exactly
    licence: str = ""  # only when it differs from the source default
    edition: str = ""  # year in the dataset title (else year published); the folder name
    coverage: str = ""  # period the data actually covers, e.g. "2015–2025"
    sha256: str = ""  # checksum of the downloaded file
    original_source: str = ""  # when the publisher redistributes another body's data
    published: str = ""  # ISO date the publisher released it (APA year); "" = n.d.
    title_translation: str = ""  # English translation of a non-English title, in APA [brackets]

    def __post_init__(self):
        get_source(self.source)
        date.fromisoformat(self.accessed)

    @property
    def licence_name(self) -> str:
        return self.licence or get_source(self.source).licence

    @property
    def has_owner(self) -> bool:
        return bool(self.owner) and self.owner != OWNER_MISSING

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Provenance":
        return cls(**d)


def meta_path(path: Path) -> Path:
    return path.with_name(path.name + ".meta.json")


def write_meta(path: Path, provenance: list[Provenance], notes: str = "") -> None:
    meta = {"sources": [p.to_dict() for p in provenance], "notes": notes}
    meta_path(path).write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")


def read_meta(path: Path) -> tuple[list[Provenance], str]:
    meta = json.loads(meta_path(path).read_text())
    return [Provenance.from_dict(d) for d in meta["sources"]], meta.get("notes", "")


def _fmt_date(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%d %b %Y").lstrip("0")


def _apa_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d:%B} {d.day}, {d.year}"


# Words kept capitalised when titles are put in APA sentence case.
PROPER = {"brunei", "darussalam", "thai", "laila", "imf", "jpes", "deps"}


def sentence_case(title: str) -> str:
    """APA sentence case: lower-case everything except the first word (and the first word
    after a colon), proper nouns in PROPER, acronyms and anything with a digit."""
    words = title.split()
    out = []
    for i, w in enumerate(words):
        bare = w.strip("()[],.:;")
        if (bare.isupper() and len(bare) > 1) or any(c.isdigit() for c in bare):
            out.append(w)  # CPI, JPES, FP.CPI.TOTL, 2025
        elif i == 0 or words[i - 1].endswith(":") or bare.lower() in PROPER:
            out.append(w[:1].upper() + w[1:].lower())
        else:
            out.append(w.lower())
    return " ".join(out)


def apa_year(p: Provenance) -> str:
    return p.published[:4] if p.published else "n.d."


def _apa_author(p: Provenance) -> str:
    return p.owner if p.has_owner else get_source(p.source).apa_author


def apa_year_labels(provenance: list[Provenance]) -> dict[Provenance, str]:
    """Year labels for one reference list. APA 7 gives works by the same author in the same
    year a suffix in title order: 2026a, 2026b, n.d.-a. Identical titles (e.g. yearly
    editions of one table) are ordered by edition."""
    groups: dict[tuple[str, str], list[Provenance]] = {}
    for p in dict.fromkeys(provenance):
        groups.setdefault((_apa_author(p) or sentence_case(p.title), apa_year(p)), []).append(p)
    labels = {}
    for (_, year), ps in groups.items():
        ps.sort(key=lambda p: (sentence_case(p.title).lower(), p.edition, p.page_url))
        for i, p in enumerate(ps):
            suffix = ("-" if year == "n.d." else "") + "abcdefghijklmnopqrstuvwxyz"[i]
            labels[p] = year + suffix if len(ps) > 1 else year
    return labels


def apa_reference(p: Provenance, html: bool = False, year: str = "") -> str:
    """APA 7 reference for a dataset, with the retrieval date the data.gov.bn terms require (M1).

    Department of Statistics, JPES. (2026). *Consumer price index 2025* [Data set].
    Brunei Open Data. Retrieved October 15, 2026, from https://...

    `year` overrides the year label, e.g. "2026a" from `apa_year_labels`.
    """
    src = get_source(p.source)
    title = sentence_case(p.title)
    title = f"<em>{escape(title)}</em>" if html else title
    if p.title_translation:  # APA 7: translation in square brackets, not italic
        title += f" [{escape(p.title_translation) if html else p.title_translation}]"
    author = _apa_author(p)
    year = f"({year or apa_year(p)})."
    head = (
        f"{author.rstrip('.')}. {year} {title} [Data set]."
        if author
        else f"{title} [Data set]. {year}"
    )
    extra = ""
    if p.original_source:
        extra += f" Original data from {p.original_source}."
    if p.source != "datagovbn":
        extra += f" Licensed under {p.licence_name}."
    url = f'<a href="{escape(p.page_url)}">{escape(p.page_url)}</a>' if html else p.page_url
    return f"{head} {src.apa_publisher}.{extra} Retrieved {_apa_date(p.accessed)}, from {url}"


attribution = apa_reference  # full credit for one dataset (DATA_USE_POLICY.md §4)


def _short_label(p: Provenance) -> str:
    year = apa_year(p)
    if p.source == "datagovbn":
        who = p.owner if p.has_owner else "data.gov.bn (owner not stated)"
        return f"{who} ({year}), via data.gov.bn" if p.has_owner else f"{who} ({year})"
    src = get_source(p.source)
    origin = f", original data from {p.original_source}" if p.original_source else ""
    return f"{src.apa_author} ({year}), {src.apa_publisher}{origin}"


def short_credit(provenance: list[Provenance]) -> str:
    """One-line chart note covering every dataset behind a chart: author (year), where it came
    from, and the date retrieved (policy M1)."""
    if not provenance:
        raise ValueError("A chart must credit at least one dataset.")
    labels: dict[str, list[str]] = {}
    for p in provenance:
        labels.setdefault(_short_label(p), []).append(p.accessed)
    parts = [f"{label}, retrieved {_fmt_date(max(d))}" for label, d in labels.items()]
    return (
        f"Source: {'; '.join(parts)}. Analysis by {BYLINE}; not an official government publication."
    )
