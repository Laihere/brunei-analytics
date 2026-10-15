"""Small processed tables that a case study hands to the dashboard.

Each CSV in case_studies/<study>/outputs/ has a .meta.json sidecar listing the
datasets behind it and what was done to them (policy M1 and M2).
"""

from pathlib import Path

import pandas as pd

from shared.provenance import Provenance, read_meta, short_credit, write_meta


def write_output(df: pd.DataFrame, path: Path, provenance: list[Provenance], notes: str) -> Path:
    if not provenance:
        raise ValueError("Outputs must list the datasets they were built from.")
    if not notes.strip():
        raise ValueError("Outputs must describe their transformations (policy M2).")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    write_meta(path, provenance, notes)
    return path


def read_output(path: Path) -> tuple[pd.DataFrame, list[Provenance], str]:
    provenance, notes = read_meta(path)
    return pd.read_csv(path), provenance, notes


def credit_for(path: Path) -> str:
    return short_credit(read_meta(path)[0])
