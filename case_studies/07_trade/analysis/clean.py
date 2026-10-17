"""Cleaning for case study 07 (trade: imports, exports and balance of trade).

The yearly totals and the commodity-section tables are published in several editions with
different owners and section labels. Sections are keyed by their SITC Rev. 3 code (0–9), as in
"Classification Of Trade Commodities". Values are BND million at current prices. See
DATA_SOURCES.md "Trade tables" known issues.
"""

from pathlib import Path

import pandas as pd

# Published measure label → key (yearly totals tables)
MEASURES = {
    "exports": "exports",
    "domestic exports": "domestic_exports",
    "re-exports": "re_exports",
    "imports": "imports",
    "total trade": "total_trade",
    "balance of trade": "balance",
    # DEPD 2009–2013 edition ("Inport, Export And Balance Of Trade")
    "export (domestic exports)": "domestic_exports",
    "export (re-exports)": "re_exports",
}
# Section names differ between editions; each is matched to its SITC code by keyword, most
# specific first ("miscellaneous manufactured" before "manufactured goods").
SECTION_KEYWORDS = [
    ("miscellaneous manufactured", 8),
    ("miscellaneous transaction", 9),
    ("food", 0),
    ("beverages", 1),
    ("crude material", 2),
    ("mineral fuel", 3),
    ("vegetable", 4),  # "Animal and Vegetable Oils and Fats", "Vegetables Oil and Animals Fats"
    ("chemicals", 5),
    ("manufactured goods", 6),
    ("machinery", 7),
]
# Short English labels for charts (the official names are kept in `section_official`).
SHORT = {
    0: "Food and live animals",
    1: "Beverages and tobacco",
    2: "Crude materials (not fuels)",
    3: "Mineral fuels",
    4: "Animal and vegetable oils",
    5: "Chemicals",
    6: "Manufactured goods",
    7: "Machinery and transport",
    8: "Other manufactured articles",
    9: "Other transactions",
}
ROUNDING = 0.15  # BND million: some values are published rounded to 0.1, others in full


def _norm(text) -> str:
    return " ".join(str(text).split()).lower()


def sitc_code(name: str) -> int:
    key = _norm(name)
    for word, code in SECTION_KEYWORDS:
        if word in key:
            return code
    raise ValueError(f"Unknown commodity section: {name!r}. Add it to SECTION_KEYWORDS.")


def load_trade(path: Path) -> pd.DataFrame:
    """Yearly totals table → one row per year: exports, domestic_exports, re_exports, imports,
    total_trade, balance (BND million). The DEPD edition has no exports or total trade column;
    they are added from its parts so every edition has the same columns."""
    df = pd.read_excel(path)
    df.columns = ["year", "measure", "value"]
    df["measure"] = df.measure.map(lambda m: MEASURES.get(_norm(m)))
    if df.measure.isna().any():
        raise ValueError(f"Unknown measures in {path.name}.")
    wide = df.pivot(index="year", columns="measure", values="value").astype(float)
    if "exports" not in wide:
        wide["exports"] = wide.domestic_exports + wide.re_exports
    if "total_trade" not in wide:
        wide["total_trade"] = wide.exports + wide.imports
    wide = wide[["exports", "domestic_exports", "re_exports", "imports", "total_trade", "balance"]]
    check_trade(wide, path.name)
    return wide.rename_axis(columns=None).reset_index().astype({"year": int})


def check_trade(wide: pd.DataFrame, name: str = "") -> None:
    """The published parts must add up, allowing for values rounded to 0.1 million."""
    gaps = {
        "exports = domestic + re-exports": wide.exports - wide.domestic_exports - wide.re_exports,
        "total trade = exports + imports": wide.total_trade - wide.exports - wide.imports,
        "balance = exports − imports": wide.balance - wide.exports + wide.imports,
    }
    for rule, gap in gaps.items():
        if (gap.abs() > ROUNDING).any():
            raise ValueError(f"{name}: {rule} fails in {list(gap[gap.abs() > ROUNDING].index)}.")


def load_sections(path: Path, flow: str) -> pd.DataFrame:
    """Commodity-section table → year, flow, sitc, value_bnd_m (one row per year and section).

    The import tables include a "Total Import" row per year; it is checked against the sum of
    the sections and then dropped.
    """
    df = pd.read_excel(path)
    df.columns = ["year", "name", "value"]
    total = df.name.map(_norm).eq("total import")
    out = df[~total].assign(sitc=lambda d: d.name.map(sitc_code))
    out = out.astype({"year": int, "value": float})
    if out.duplicated(["year", "sitc"]).any():
        raise ValueError(f"{path.name}: a section appears twice in one year.")
    if (out.groupby("year").sitc.nunique() != 10).any():
        raise ValueError(f"{path.name}: a year is missing a section.")
    if total.any():
        published = df[total].astype({"year": int}).set_index("year").value.astype(float)
        gap = (out.groupby("year").value.sum() - published).abs()
        if (gap > ROUNDING).any():
            raise ValueError(f"{path.name}: sections don't add up to 'Total Import'.")
    out = out.rename(columns={"value": "value_bnd_m"}).assign(flow=flow)
    return out[["year", "flow", "sitc", "value_bnd_m"]].sort_values(["year", "sitc"])


def load_classification(path: Path) -> pd.DataFrame:
    """SITC Rev. 3 section key: sitc, section_official (English), section_ms (Malay), section.

    The sheet lists each section as "( n )  Malay name" followed by its English name.
    """
    lines = [" ".join(str(v).split()) for v in pd.read_excel(path, header=None)[0].dropna()]
    rows = []
    for i, line in enumerate(lines):
        if line.startswith("(") and ")" in line[:6]:
            code = int(line[1 : line.index(")")].strip())
            rows.append(
                {
                    "sitc": code,
                    "section_official": lines[i + 1],
                    "section_ms": line[line.index(")") + 1 :].strip(),
                    "section": SHORT[code],
                }
            )
    key = pd.DataFrame(rows)
    if sorted(key.sitc) != list(range(10)):
        raise ValueError("Expected SITC sections 0–9 in the classification table.")
    return key


def compare_editions(main: pd.DataFrame, other: pd.DataFrame, on: list[str]) -> pd.DataFrame:
    """Values that differ by more than rounding between two editions, for shared rows."""
    value = [c for c in main.columns if c not in on]
    m = main.merge(other, on=on, suffixes=("", "_other"))
    rows = []
    for col in value:
        gap = (m[col] - m[f"{col}_other"]).abs()
        for _, r in m[gap > ROUNDING].iterrows():
            rows.append(
                {**{k: r[k] for k in on}, "column": col, "main": r[col], "other": r[f"{col}_other"]}
            )
    return pd.DataFrame(rows, columns=[*on, "column", "main", "other"])
