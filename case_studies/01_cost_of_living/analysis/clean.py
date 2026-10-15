"""Cleaning for case study 01 (cost of living in 2025).

Repairs follow DATA_SOURCES.md "Known issues". Each repair is checked against the publisher's
own percentage-change table, and every repaired value is flagged in the output.
"""

from pathlib import Path

import pandas as pd

OVERALL = "Overall CPI"
TOLERANCE_PTS = 0.25  # max gap between implied and published % change after repair


def _read(path: Path, value: str) -> pd.DataFrame:
    df = pd.read_excel(path).dropna(how="all")
    df.columns = ["year", "category", value]  # CPI file heads the index column "Weight"
    df["year"] = df["year"].astype(int)
    df["category"] = df["category"].str.strip()
    return df


def load_cpi(index_path: Path, pct_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    return _read(index_path, "index"), _read(pct_path, "pct_change")


def repair_cpi(index: pd.DataFrame, pct: pd.DataFrame) -> pd.DataFrame:
    """Fix the shifted 2023 rows and the 2022 overall value (DATA_SOURCES.md CPI issues 1–2).

    Both are rebuilt as previous year × (1 + published % change). Returns long format with a
    `repaired` flag. Raises if any year still disagrees with the published changes.
    """
    wide = index.pivot(index="year", columns="category", values="index")
    change = pct.pivot(index="year", columns="category", values="pct_change")
    fixed = wide.copy()
    repaired = pd.DataFrame(False, index=wide.index, columns=wide.columns)

    categories_2023 = [c for c in wide.columns if c != OVERALL]
    fixed.loc[2023, categories_2023] = wide.loc[2022, categories_2023] * (
        1 + change.loc[2023, categories_2023] / 100
    )
    repaired.loc[2023, categories_2023] = True
    fixed.loc[2022, OVERALL] = wide.loc[2021, OVERALL] * (1 + change.loc[2022, OVERALL] / 100)
    repaired.loc[2022, OVERALL] = True

    gap = ((fixed.pct_change() * 100) - change).abs().max().max()
    if gap > TOLERANCE_PTS:
        raise ValueError(f"Repaired CPI still differs from published % change by {gap:.2f} pts.")

    out = fixed.stack().rename("index").reset_index()
    out["repaired"] = repaired.stack().values
    return out.sort_values(["category", "year"]).reset_index(drop=True)


ITEM_EXCLUDE = {"Saloon Car (1,500cc)"}  # not a household staple; no data after 2019
ITEM_FLAGS = {("Sugar (Per Kilogramme)", 2024): "Implausible: 1.30 in 2022, 2023 and 2025"}


def load_items(path: Path) -> pd.DataFrame:
    """Subsidised and price-controlled items, BND. Flags rather than drops doubtful values."""
    df = _read(path, "price_bnd")
    df = df.rename(columns={"category": "item"})
    df = df[~df["item"].isin(ITEM_EXCLUDE)].copy()
    df["flag"] = [ITEM_FLAGS.get((i, y), "") for i, y in zip(df["item"], df["year"], strict=True)]
    return df.sort_values(["item", "year"]).reset_index(drop=True)
