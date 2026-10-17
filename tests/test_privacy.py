"""No small counts in published outputs (DATA_USE_POLICY.md §8, rule 3)."""

import pandas as pd
import pytest

from shared.paths import CASE_STUDIES

OUTPUTS = sorted(CASE_STUDIES.glob("[0-9]*/outputs/*.csv"))

# Counts of people, incidents or businesses: no value from 1 to 5 may be published.
COUNTS = {
    "accidents",
    "arrests",
    "businesses",
    "cases",
    "deaths",
    "deaths_fire_rescue",
    "deaths_police",
    "employees",
    "fires",
    "fires_main",
    "fires_other",
    "injuries",
    "injuries_fire_rescue",
    "injuries_police",
    "solved",
}
# Whole-number columns that are not counts of people, incidents or businesses.
NOT_COUNTS = {
    "year",
    "years",
    "sitc",  # trade commodity section code, 0–9
    "shared_years",  # edition cross-checks
    "differences",
}

# (output file name, column, row label) → reason a small value is allowed. Keep it short.
ALLOWED: dict[tuple[str, str, str], str] = {}


def _is_whole_number(s: pd.Series) -> bool:
    s = s.dropna()
    return (
        len(s) > 0
        and pd.api.types.is_numeric_dtype(s)
        and not pd.api.types.is_bool_dtype(s)
        and (s == s.round()).all()
    )


def test_outputs_found():
    assert len(OUTPUTS) >= 20


@pytest.mark.parametrize("path", OUTPUTS, ids=lambda p: f"{p.parts[-3]}/{p.name}")
def test_every_whole_number_column_is_classified(path):
    """A new column must be added to COUNTS or NOT_COUNTS, so no count slips through."""
    df = pd.read_csv(path)
    unclassified = [
        c for c in df.columns if _is_whole_number(df[c]) and c not in COUNTS | NOT_COUNTS
    ]
    assert not unclassified, f"Add to COUNTS or NOT_COUNTS in tests/test_privacy.py: {unclassified}"


@pytest.mark.parametrize("path", OUTPUTS, ids=lambda p: f"{p.parts[-3]}/{p.name}")
def test_no_counts_from_one_to_five(path):
    df = pd.read_csv(path)
    small = []
    for col in COUNTS & set(df.columns):
        for i, value in df[col].items():
            if 0 < value <= 5:
                label = " · ".join(str(v) for v in df.loc[i].drop(list(COUNTS), errors="ignore"))
                if (path.name, col, label) not in ALLOWED:
                    small.append((col, label, value))
    assert not small, f"Merge or suppress these cells (policy §8): {small}"
