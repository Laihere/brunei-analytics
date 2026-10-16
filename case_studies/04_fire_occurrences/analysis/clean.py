"""Cleaning for case study 04 (fire occurrences by district).

The 2009–2020 edition is the main source. The 2009–2013 edition is a cross-check, and the
forest and grass fire table (hectares burned) is compared by year pattern only.
See DATA_SOURCES.md "Fire Occurances By Districts" known issues.
"""

from pathlib import Path

import pandas as pd

DISTRICTS = {  # as published → official spelling
    "Brunei Muara": "Brunei-Muara",
    "Belait": "Belait",
    "Tutong": "Tutong",
    "Temburong": "Temburong",
}
KNOWN_DIFFERENT_YEARS = {2013}  # DATA_SOURCES.md fire issue 2: the editions disagree


def load_fires(path: Path) -> pd.DataFrame:
    """(Year, District, Amount) → year, district, fires. Raises if a district is renamed or
    missing, a year-district appears twice, or a year is skipped."""
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df["District"] = df["District"].str.strip()
    if set(df["District"]) != set(DISTRICTS):
        raise ValueError(f"Unexpected districts: {sorted(set(df['District']))}")
    if df.duplicated(["Year", "District"]).any():
        raise ValueError("A district appears twice in a year.")
    if (df.groupby("Year")["District"].nunique() != len(DISTRICTS)).any():
        raise ValueError("A year is missing a district.")
    years = sorted(df["Year"].unique())
    if years != list(range(years[0], years[-1] + 1)):
        raise ValueError("Years are not consecutive.")
    out = pd.DataFrame(
        {
            "year": df["Year"].astype(int),
            "district": df["District"].map(DISTRICTS),
            "fires": df["Amount"].astype(int),
        }
    )
    return out.sort_values(["year", "district"]).reset_index(drop=True)


def compare_editions(main: pd.DataFrame, other: pd.DataFrame) -> pd.DataFrame:
    """Yearly totals of both editions for the years they share. Raises if any district differs
    in a year not listed in KNOWN_DIFFERENT_YEARS."""
    both = main.merge(other, on=["year", "district"], suffixes=("_main", "_other"))
    differ = both[both.fires_main != both.fires_other]
    unexpected = set(differ.year) - KNOWN_DIFFERENT_YEARS
    if unexpected:
        raise ValueError(f"Editions disagree in {sorted(unexpected)}; record it before going on.")
    out = both.groupby("year", as_index=False)[["fires_main", "fires_other"]].sum()
    out["same_by_district"] = ~out.year.isin(differ.year)
    return out


def load_area(path: Path) -> pd.DataFrame:
    """Forest and grass/peat fire table → year, forest_ha, grass_peat_ha, total_ha."""
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df["TYPE"] = df["TYPE"].str.strip()
    wide = df.pivot(index="YEAR", columns="TYPE", values="HECTRES")
    wide = wide.rename(columns={"FOREST FIRE": "forest_ha", "GRASS/PEAT FIRE": "grass_peat_ha"})
    if set(wide.columns) != {"forest_ha", "grass_peat_ha"} or wide.isna().any().any():
        raise ValueError("Expected one forest and one grass/peat value for every year.")
    wide["total_ha"] = wide.forest_ha + wide.grass_peat_ha
    wide = wide.rename_axis("year").reset_index()
    wide.columns.name = None
    return wide
