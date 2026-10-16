"""Cleaning for case study 06 (livestock supply, Agriculture and Agrifood Department).

Each "industry" table gives local production and imports by year. They are combined into one
long table: year, product, local, imports, local share. See DATA_SOURCES.md "Livestock industry
tables" known issues.
"""

from pathlib import Path

import pandas as pd

# product key → (label, unit, local column, import columns), columns as published (trimmed)
PRODUCTS = {
    "chicken": ("Chicken meat", "tonnes", "Local Production (mt)", ["Import (mt)"]),
    "eggs": (
        "Eggs",
        "million eggs",
        "Monthly Production (Million Eggs)",  # yearly values despite the label (issue 5)
        ["Import (Million Eggs)"],
    ),
    "beef": (
        "Beef",
        "tonnes",
        "Local Production (mt)",
        ["Import (Alive) (mt)", "Import (Chilled & Frozen) (mt)"],
    ),
    "chicks": ("Day-old chicks", "birds", "Local Production (Birds)", ["Import (Birds)"]),
    "hatching_eggs": (
        "Fertilized (hatching) eggs",
        "eggs",
        "Local Production (Eggs)",
        ["Import (Eggs)"],
    ),
}
KG_PER_BIRD = 1.5  # issue 2: local chicken tonnes = birds slaughtered × 1.5 kg


def read_table(path: Path) -> pd.DataFrame:
    """A published industry table with blank spacer columns removed and names trimmed."""
    df = pd.read_excel(path)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")].dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    return df.astype({"Year": int}).set_index("Year").sort_index()


def supply(product: str, path: Path) -> pd.DataFrame:
    """One product → year, product, label, unit, local, imports (+ each import type), local_share.

    Years with any "n/a" are dropped. Raises if a column is missing or years are skipped.
    """
    label, unit, local_col, import_cols = PRODUCTS[product]
    df = read_table(path)
    missing = [c for c in [local_col, *import_cols] if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name}: missing columns {missing}")
    num = df[[local_col, *import_cols]].apply(pd.to_numeric, errors="coerce").dropna()
    years = num.index.tolist()
    if years != list(range(years[0], years[-1] + 1)):
        raise ValueError(f"{path.name}: years are not consecutive.")
    out = pd.DataFrame(
        {
            "year": num.index,
            "product": product,
            "label": label,
            "unit": unit,
            "local": num[local_col].values,
            "imports": num[import_cols].sum(axis=1).values,
        }
    )
    if len(import_cols) > 1:  # beef: keep the two import types
        out["imports_alive"] = num[import_cols[0]].values
        out["imports_chilled_frozen"] = num[import_cols[1]].values
    out["local_share_pct"] = out.local / (out.local + out.imports) * 100
    return out


def compare_editions(new: Path, old: Path, known: dict[int, str] | None = None) -> pd.DataFrame:
    """Years where two editions of a table differ. Raises on a difference not in `known`
    ({year: reason}); returns the known ones for the record."""
    a, b = read_table(new), read_table(old)
    years = a.index.intersection(b.index)
    a = a.loc[years].apply(pd.to_numeric, errors="coerce")
    b = b.loc[years, a.columns].apply(pd.to_numeric, errors="coerce")
    differ = ((a - b).abs() > 0.01).any(axis=1)
    unexpected = set(differ[differ].index) - set(known or {})
    if unexpected:
        raise ValueError(f"{new.name}: editions differ in {sorted(unexpected)}; log it first.")
    rows = [
        {
            "table": new.name,
            "year": y,
            "column": c,
            "new_edition": a.loc[y, c],
            "old_edition": b.loc[y, c],
        }
        for y in differ[differ].index
        for c in a.columns
        if abs(a.loc[y, c] - b.loc[y, c]) > 0.01
    ]
    return pd.DataFrame(rows, columns=["table", "year", "column", "new_edition", "old_edition"])


def slaughter_check(slaughter: Path, chicken: pd.DataFrame) -> pd.DataFrame:
    """Birds slaughtered per year (published totals) and local chicken tonnes ÷ birds.

    Raises unless every year's tonnes equal birds × KG_PER_BIRD (issue 2), which also shows the
    published totals are the ones consistent with the meat figures.
    """
    df = read_table(slaughter)
    out = pd.DataFrame({"year": df.index, "birds": df["Total"].values})
    out = out.merge(chicken[["year", "local"]], on="year")
    out["kg_per_bird"] = out.local * 1000 / out.birds
    if ((out.kg_per_bird - KG_PER_BIRD).abs() > 0.001).any():
        raise ValueError("Chicken tonnes are no longer birds × 1.5 kg; revisit issue 2.")
    months = df.drop(columns="Total").sum(axis=1)
    out["months_sum"] = months.values
    out["months_match_total"] = (months - df["Total"]).abs().values < 1
    return out.rename(columns={"local": "local_tonnes"})
