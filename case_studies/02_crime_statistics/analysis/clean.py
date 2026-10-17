"""Cleaning for case study 02 (crime statistics).

Reads the Royal Brunei Police Force yearbook table (e.g. table 14.2, "Crime Statistics, 2012").
Rows are found by their labels, not fixed positions, so another edition with a different list
of Acts parses the same way. See DATA_SOURCES.md "Crime Statistics" known issues.
"""

import re
from pathlib import Path

import openpyxl
import pandas as pd

POLICE = "police"
OTHER = "other agencies"
SECTIONS = {"Cases Handled By Police": POLICE, "Cases Handled By Other Agencies": OTHER}
COUNTS = ["cases", "solved", "arrests"]  # columns B, C and E; D is the published solved %
MIN_CASES = 5  # SOP 7: Acts with fewer cases than this in any year go into "Other Acts"
OTHER_ACTS = "Other Acts"
OTHER_ACTS_MS = "Akta-akta lain"


def _label(v) -> str:
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def _count(v) -> float:
    """Published counts. "-" isn't explained in the source, so it is read as missing."""
    if v is None or (isinstance(v, str) and v.strip() in {"", "-"}):
        return float("nan")
    return float(v)


def read_table(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """One yearbook file → (rows, published totals), both long format.

    Each data row is a Malay label with the counts, followed by its English label on the next
    row. Stored cell values are used, since totals and % are Excel formulas.
    """
    ws = openpyxl.load_workbook(path, data_only=True).active
    rows = [[c.value for c in r[:5]] for r in ws.iter_rows()]
    title = " ".join(_label(r[0]) for r in rows[:3])
    year = int(re.search(r"Crime Statistics,\s*(\d{4})", title).group(1))

    records, totals, section = [], [], None
    for i, (a, b, c, _, e) in enumerate(rows):
        label = _label(a)
        if label in SECTIONS:
            section = SECTIONS[label]
            continue
        is_count = isinstance(b, int | float) or (isinstance(b, str) and b.strip() == "-")
        if section is None or not label or not is_count:  # headers, English rows, blanks
            continue
        values = dict(zip(COUNTS, (_count(b), _count(c), _count(e)), strict=True))
        if label == "Jumlah":
            totals.append({"year": year, "handled_by": section, **values})
            continue
        english = _label(rows[i + 1][0])
        records.append(
            {"year": year, "handled_by": section, "offence": english, "offence_ms": label} | values
        )
    return pd.DataFrame(records), pd.DataFrame(totals)


def check_totals(rows: pd.DataFrame, totals: pd.DataFrame) -> None:
    """Rows must add up to the published total rows (which count "-" as zero)."""
    summed = rows.groupby(["year", "handled_by"])[COUNTS].sum(min_count=0)
    published = totals.set_index(["year", "handled_by"])[COUNTS]
    gap = (summed - published).abs().max().max()
    if gap > 0:
        raise ValueError(f"Rows don't add up to the published totals (largest gap {gap:.0f}).")


def merge_small(rows: pd.DataFrame, min_cases: int = MIN_CASES) -> pd.DataFrame:
    """Merge other-agency Acts with fewer than `min_cases` in any year (or missing in a year)
    into "Other Acts", so every year shows the same rows and no count is below the limit.

    `complete` is False when a merged or kept value includes a "-" cell, so its solved and
    arrest counts are a lower bound.
    """
    other = rows[rows.handled_by == OTHER]
    years = rows.year.nunique()
    by_act = other.groupby("offence")["cases"]
    keep = set(by_act.min()[(by_act.min() >= min_cases) & (by_act.count() == years)].index)

    out = rows.copy()
    small = (out.handled_by == OTHER) & ~out.offence.isin(keep)
    out.loc[small, ["offence", "offence_ms"]] = [OTHER_ACTS, OTHER_ACTS_MS]
    out["complete"] = out[COUNTS].notna().all(axis=1)
    out = out.groupby(
        ["year", "handled_by", "offence", "offence_ms"], as_index=False, sort=False
    ).agg(
        cases=("cases", "sum"),
        solved=("solved", lambda s: s.sum(min_count=1)),
        arrests=("arrests", lambda s: s.sum(min_count=1)),
        complete=("complete", "all"),
    )
    merged_cases = out.loc[out.offence == OTHER_ACTS, "cases"]
    if (merged_cases < min_cases).any():
        raise ValueError("'Other Acts' itself is below the small-count limit.")
    return out


def load_unmerged(paths: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """All editions → (every row as published, checked against the totals; published totals).

    These rows include small counts, so they are kept locally only (data/clean/).
    """
    parts = [read_table(p) for p in paths]
    rows = pd.concat([r for r, _ in parts], ignore_index=True)
    totals = pd.concat([t for _, t in parts], ignore_index=True)
    check_totals(rows, totals)
    return rows, totals


def load(paths: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """All editions → (rows with small Acts merged, published totals)."""
    rows, totals = load_unmerged(paths)
    return merge_small(rows), totals
