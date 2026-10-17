"""Cleaning for case study 08 (Muara Port: containers and uncontainerised cargo, 2004–2015).

Both tables are one row per year with blank spacer columns. The Ports Department's data
definitions say total containers = local + transhipment, but the published totals differ from
that sum in most years; both are kept and the gap is reported. See DATA_SOURCES.md "Muara Port
tables" known issues.
"""

from pathlib import Path

import pandas as pd

# Published column → key (names trimmed)
CONTAINER_COLUMNS = {
    "Local Containers (TEUs)": "local_teu",
    "Transhipment Containers (TEUs)": "transhipment_teu",
    "Total Containers (TEUs)": "total_published_teu",
}
CARGO_COLUMNS = {"Uncontainerized Cargo (Tonnage)": "cargo_tonnes"}


def _read(path: Path, columns: dict[str, str]) -> pd.DataFrame:
    """A port table with spacer columns dropped, names trimmed and mapped to keys."""
    df = pd.read_excel(path)
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in ["Year", *columns] if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name}: missing columns {missing}")
    df = df[["Year", *columns]].rename(columns={"Year": "year", **columns})
    df = df.dropna(subset=["year"]).astype({"year": int})
    if df.year.duplicated().any() or (df.year.diff().dropna() != 1).any():
        raise ValueError(f"{path.name}: years must be unique and consecutive.")
    return df.reset_index(drop=True)


def load_containers(path: Path) -> pd.DataFrame:
    """year, local_teu, transhipment_teu, total_published_teu, total_teu (local +
    transhipment, as the data definition describes), gap_teu (published − sum)."""
    df = _read(path, CONTAINER_COLUMNS).astype({c: float for c in CONTAINER_COLUMNS.values()})
    if (df[list(CONTAINER_COLUMNS.values())] < 0).any().any():
        raise ValueError(f"{path.name}: negative container counts.")
    df["total_teu"] = df.local_teu + df.transhipment_teu
    df["gap_teu"] = df.total_published_teu - df.total_teu
    df["transhipment_share_pct"] = df.transhipment_teu / df.total_teu * 100
    return df


def load_cargo(path: Path) -> pd.DataFrame:
    """year, cargo_tonnes (uncontainerised cargo handled at Muara Conventional Terminal)."""
    df = _read(path, CARGO_COLUMNS).astype({"cargo_tonnes": float})
    if (df.cargo_tonnes <= 0).any():
        raise ValueError(f"{path.name}: cargo must be positive in every year.")
    return df
