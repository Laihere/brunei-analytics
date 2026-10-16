"""Cleaning for case study 03 (road casualties).

Police "Road Casualties" is the main source. Fire and Rescue "Statistics of Road Traffic
Accidents" covers only accidents its crews attended, so it is used as a check, never charted.
See DATA_SOURCES.md "Road Casualties" known issues.
"""

from pathlib import Path

import pandas as pd

MEASURES = {"Accidents": "accidents", "Injuries": "injuries", "Deaths": "deaths"}
PERIOD_YEARS = 3  # deaths swing a lot from year to year, so compare 3-year averages


def load_police(path: Path) -> pd.DataFrame:
    """Long (Year, Type, Amount) → one row per year with accidents, injuries and deaths.

    Raises if the types change, a year has a duplicate or missing measure, or years are skipped.
    """
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df["Type"] = df["Type"].str.strip()
    if set(df["Type"]) != set(MEASURES):
        raise ValueError(f"Unexpected types: {sorted(set(df['Type']))}")
    if df.duplicated(["Year", "Type"]).any():
        raise ValueError("A year has the same measure twice.")
    wide = df.pivot(index="Year", columns="Type", values="Amount").rename(columns=MEASURES)
    if wide.isna().any().any():
        raise ValueError("A year is missing a measure.")
    years = wide.index.to_list()
    if years != list(range(min(years), max(years) + 1)):
        raise ValueError("Years are not consecutive.")
    wide = wide[list(MEASURES.values())].astype(int).rename_axis("year").reset_index()
    wide.columns.name = None
    return wide


def load_fire_rescue(path: Path) -> pd.DataFrame:
    """Fire and Rescue table → deaths and injuries per year, both call types summed.

    The header sits on the second row and each year is a merged cell over two rows.
    """
    df = pd.read_excel(path, header=1)
    df.columns = df.columns.str.strip()
    df["YEAR"] = df["YEAR"].ffill().astype(int)
    out = df.groupby("YEAR", as_index=False)[["DEAD", "INJURED"]].sum()
    return out.rename(columns={"YEAR": "year", "DEAD": "deaths", "INJURED": "injuries"})


def add_ratios(roads: pd.DataFrame) -> pd.DataFrame:
    out = roads.copy()
    out["injuries_per_100_accidents"] = out.injuries / out.accidents * 100
    out["deaths_per_1000_accidents"] = out.deaths / out.accidents * 1000
    return out


def periods(roads: pd.DataFrame, size: int = PERIOD_YEARS) -> pd.DataFrame:
    """Yearly averages over consecutive blocks of `size` years, from the first year.

    Raises if the years don't divide into whole blocks, so no period is an average of fewer years.
    """
    first, n = roads.year.min(), len(roads)
    if n % size:
        raise ValueError(f"{n} years don't split into {size}-year periods.")
    block = (roads.year - first) // size
    label = block.map(lambda b: f"{first + b * size}–{first + b * size + size - 1}")
    avg = roads.groupby(label, sort=False)[["accidents", "injuries", "deaths"]].mean()
    avg = add_ratios(avg.reset_index(names="period"))
    avg.insert(1, "years", size)
    return avg
